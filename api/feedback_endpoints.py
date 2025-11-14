"""
LLM-Powered Feedback Collection Endpoints
To be imported into main.py
"""

# This content will be added to main.py

FEEDBACK_ENDPOINTS = '''
# ============================================
# LLM-Powered Feedback Collection
# ============================================

@app.post("/feedback/start")
async def start_feedback_session(
    meeting_id: str,
    user_id: str,
    startup_id: Optional[str] = None,
    startup_name: str = "",
    startup_description: str = "",
    db: Session = Depends(get_db)
):
    """
    Start a new LLM-powered feedback session
    - Generates 3 contextual questions about the startup meeting
    - Creates a feedback session
    - Returns first question to start the conversation
    """
    # Check if session already exists
    existing = db.query(models.FeedbackSession).filter(
        models.FeedbackSession.meetingId == meeting_id,
        models.FeedbackSession.userId == user_id,
        models.FeedbackSession.status == "in_progress"
    ).first()

    if existing:
        # Resume existing session
        questions = existing.questions
        current_idx = existing.current_question_index

        return {
            "session_id": existing.id,
            "resumed": True,
            "current_question": questions[current_idx] if current_idx < len(questions) else None,
            "progress": {
                "current": current_idx + 1,
                "total": len(questions),
                "answered": current_idx
            },
            "conversation_history": existing.conversation_history
        }

    # Generate 3 contextual questions using LLM
    questions = await feedback_assistant.generate_questions(
        startup_name=startup_name,
        startup_description=startup_description,
        meeting_context=f"Meeting ID: {meeting_id}"
    )

    # Create new feedback session
    session = models.FeedbackSession(
        meetingId=meeting_id,
        userId=user_id,
        startupId=startup_id,
        startupName=startup_name,
        questions=questions,
        answers={},
        conversation_history=[],
        current_question_index=0,
        status="in_progress"
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    # Generate first message
    first_response = await feedback_assistant.process_conversation_turn(
        message="",
        conversation_history=[],
        current_question=questions[0],
        is_first_message=True
    )

    # Add to conversation history
    session.conversation_history.append({
        "role": "assistant",
        "content": first_response["response"],
        "timestamp": datetime.utcnow().isoformat()
    })
    db.commit()

    return {
        "session_id": session.id,
        "resumed": False,
        "message": first_response["response"],
        "current_question": questions[0],
        "progress": {
            "current": 1,
            "total": len(questions),
            "answered": 0
        }
    }

@app.post("/feedback/chat", response_model=schemas.FeedbackChatResponse)
async def chat_feedback(
    message_data: schemas.FeedbackChatMessage,
    db: Session = Depends(get_db)
):
    """
    Process a user message in the feedback chat
    - Accepts user's answer to current question
    - Moves to next question or completes session
    - Returns conversational response
    """
    session = db.query(models.FeedbackSession).filter(
        models.FeedbackSession.id == message_data.session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Feedback session not found")

    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Session already completed")

    # Add user message to history
    session.conversation_history.append({
        "role": "user",
        "content": message_data.message,
        "timestamp": datetime.utcnow().isoformat()
    })

    current_idx = session.current_question_index
    questions = session.questions

    # Save answer for current question
    current_question = questions[current_idx]
    session.answers[str(current_question["id"])] = {
        "question": current_question["question"],
        "answer": message_data.message,
        "category": current_question["category"]
    }

    # Process with LLM
    response_data = await feedback_assistant.process_conversation_turn(
        message=message_data.message,
        conversation_history=session.conversation_history,
        current_question=current_question,
        is_first_message=False
    )

    # Add assistant response to history
    session.conversation_history.append({
        "role": "assistant",
        "content": response_data["response"],
        "timestamp": datetime.utcnow().isoformat()
    })

    # Move to next question
    next_idx = current_idx + 1

    if next_idx >= len(questions):
        # All questions answered - complete session
        session.status = "completed"
        session.completed_at = datetime.utcnow()

        # Generate completion summary
        qa_pairs = [
            {
                **session.answers[str(q["id"])],
                "question": q["question"],
                "category": q["category"]
            }
            for q in questions
        ]

        completion_message = await feedback_assistant.generate_completion_summary(
            startup_name=session.startupName,
            qa_pairs=qa_pairs
        )

        # Create meeting insight from Q&A
        insight_data = feedback_assistant.format_insights_for_storage(
            qa_pairs=qa_pairs,
            meeting_id=session.meetingId,
            startup_id=session.startupId or "",
            startup_name=session.startupName,
            user_id=session.userId
        )

        # Save insight
        insight = models.MeetingInsight(**insight_data)
        db.add(insight)

        db.commit()

        return schemas.FeedbackChatResponse(
            response=f"{response_data['response']}\\n\\n{completion_message}",
            question_id=None,
            current_question=None,
            progress={
                "current": len(questions),
                "total": len(questions),
                "answered": len(questions)
            },
            session_id=session.id,
            completed=True
        )

    # Move to next question
    session.current_question_index = next_idx
    next_question = questions[next_idx]

    # Ask next question
    next_message = f"\\n\\n**Question {next_idx + 1} of {len(questions)}:**\\n{next_question['question']}"
    combined_response = response_data["response"] + next_message

    session.conversation_history.append({
        "role": "assistant",
        "content": next_message,
        "timestamp": datetime.utcnow().isoformat()
    })

    session.last_interaction = datetime.utcnow()
    db.commit()

    return schemas.FeedbackChatResponse(
        response=combined_response,
        question_id=next_question["id"],
        current_question=next_question,
        progress={
            "current": next_idx + 1,
            "total": len(questions),
            "answered": next_idx
        },
        session_id=session.id,
        completed=False
    )

@app.get("/feedback/session/{session_id}", response_model=schemas.FeedbackSession)
async def get_feedback_session(session_id: int, db: Session = Depends(get_db)):
    """
    Get feedback session details
    - Returns full conversation history
    - Shows progress and answers
    """
    session = db.query(models.FeedbackSession).filter(
        models.FeedingSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session

@app.put("/insights/{insight_id}/edit")
async def edit_insight(
    insight_id: int,
    updated_qa: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Edit a previously submitted insight
    - Allows updating the Q&A pairs
    - Re-generates insight text from updated answers
    """
    insight = db.query(models.MeetingInsight).filter(
        models.MeetingInsight.id == insight_id
    ).first()

    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")

    # Update structured Q&A
    insight.structured_qa = updated_qa

    # Regenerate insight text
    insight_text = "\\n\\n".join([
        f"**{qa['category'].upper()}**: {qa['question']}\\n{qa['answer']}"
        for qa in updated_qa
    ])

    insight.insight = insight_text
    insight.timestamp = datetime.utcnow()  # Update timestamp

    db.commit()
    db.refresh(insight)

    return {
        "success": True,
        "insight_id": insight_id,
        "updated_at": insight.timestamp.isoformat()
    }

@app.get("/feedback/preview/{meeting_id}")
async def preview_feedback_questions(
    meeting_id: str,
    startup_name: str,
    startup_description: str
):
    """
    Preview the 3 questions that would be generated for a meeting
    - Does not create a session
    - Useful for showing users what to expect
    """
    questions = await feedback_assistant.generate_questions(
        startup_name=startup_name,
        startup_description=startup_description,
        meeting_context=None
    )

    return {
        "meeting_id": meeting_id,
        "startup_name": startup_name,
        "questions": questions,
        "total": len(questions)
    }
'''
