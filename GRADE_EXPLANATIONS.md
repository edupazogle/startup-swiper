# Grade Explanations Implementation

## Overview
Enhanced the `evaluator/recalculate_scores.py` script to include a new `grade_explanation` parameter that provides creative, concise phrases explaining each startup's grade.

## Changes Made

### 1. New `get_grade_explanation()` Function
**Location**: `evaluator/recalculate_scores.py` (lines 397-469)

Generates context-aware explanation phrases for each grade (A+ to F):

```python
def get_grade_explanation(grade: Grade, profile: Dict) -> str:
    """Generate creative, short phrase explaining why a startup received this grade"""
```

**Features**:
- Grade-specific explanation library (5+ options per grade)
- Context-aware modifiers based on startup profile:
  - `(underfunded)` - Less than $5M funding
  - `(no B2B yet)` - No B2B business model
  - `(narrow)` - Only single use case
  - `(geo risk)` - Located outside key markets

### 2. Updated `calculate_startup_grade()` Function
**Returns**: Now includes grade_explanation as 4th return value
```python
def calculate_startup_grade(startup: Startup, verbose: bool = False) -> Tuple[Grade, float, str, str]:
    """
    Returns: (Grade, Score, Reasoning, Grade Explanation)
    """
    grade, score, reasoning = evaluate_with_llm(profile, verbose=verbose)
    grade_explanation = get_grade_explanation(grade, profile)
    return grade, score, reasoning, grade_explanation
```

### 3. Updated `GradeResult` Dataclass
**Simplified output schema**:
```python
@dataclass
class GradeResult:
    startup_id: int
    startup_name: str
    grade: str
    grade_explanation: str  # NEW
    evaluation_date: str
```

### 4. Updated Async Evaluation Method
**Method**: `ParallelGradeEvaluator._evaluate_batch_async()`

Now includes grade_explanation in results:
```python
results.append({
    'startup_id': startup.id,
    'startup_name': startup.company_name,
    'grade': grade.value,
    'grade_explanation': grade_explanation,  # NEW
    'evaluation_date': datetime.now().isoformat()
})
```

## Output Format

### JSON Schema
```json
[
  {
    "startup_id": 2,
    "startup_name": "Cognita",
    "grade": "B",
    "grade_explanation": "Workable solution (underfunded)"
  },
  {
    "startup_id": 3,
    "startup_name": "Hyphorest",
    "grade": "C+",
    "grade_explanation": "Early stage challenges"
  }
]
```

### Four Fields Only
1. **startup_id** - Unique database identifier
2. **startup_name** - Company name
3. **grade** - A+ through F (AXA Partnership Grade)
4. **grade_explanation** - Creative short phrase (15-40 chars)

## Grade Explanation Examples

| Grade | Example Explanations |
|-------|----------------------|
| **A+** | Enterprise powerhouse, Proven platform leader, Strategic multi-use case |
| **A** | Solid growth trajectory, Multi-use case potential, Strong market validation |
| **A-** | Good partnership fit, Growth-stage player, Credible offering |
| **B+** | Viable but developing, Growth potential clear, Planning required |
| **B** | Workable solution, Execution-dependent, Manageable risk |
| **B-** | Early scaling risk, Limited market fit, Needs maturation |
| **C+** | Early stage challenges, Significant gaps, High execution risk |
| **C** | Pre-growth limitations, Minimal traction, Major validation needed |
| **C-** | Prototype-stage focus, Critical gaps remain, Unproven model |
| **D** | Very early concept, Limited capabilities, Wrong fit entirely |
| **F** | Not a viable partner, Critical dealbreaker, Fundamentally misaligned |

## Contextual Modifiers

The system adds context-aware qualifiers to explanations:

- **(underfunded)** - If funding < $5M and grade is B/B+
- **(no B2B yet)** - If no B2B business model and grade is A+/A/A-
- **(narrow)** - If only 1 use case and grade is A/A-
- **(geo risk)** - If located outside major markets and grade is A+/A

### Examples with Modifiers
- "Solid growth trajectory (underfunded)"
- "Good partnership fit (no B2B yet)"
- "Enterprise powerhouse (geo risk)"

## Performance Enhancements Preserved

The implementation maintains all parallelization features:
- ✅ Async workers (configurable count)
- ✅ Batch evaluation (configurable size)
- ✅ Periodic checkpointing
- ✅ Resume capability
- ✅ Multi-worker parallelism

## Usage

### Basic Run
```bash
python3 evaluator/recalculate_scores.py --limit 100
```

### With Custom Parameters
```bash
python3 evaluator/recalculate_scores.py \
  --workers 5 \
  --batch-size 3 \
  --limit 500 \
  --output downloads/my_grades.json
```

### Resume from Checkpoint
```bash
python3 evaluator/recalculate_scores.py --resume
```

## Sample Output

```bash
$ python3 evaluator/recalculate_scores.py --limit 5

1. Cognita                    -> B   | Workable solution (underfunded)
2. Hyphorest                  -> C+  | Early stage challenges
3. DATATOENERGY               -> D   | Very early concept
4. varmo                      -> C-  | Prototype-stage focus
5. Matillion                  -> A-  | Good partnership fit

✅ Generated 5 results
```

## Files Modified
- `evaluator/recalculate_scores.py` - Added grade explanation function and updated evaluation flow

## Dependencies
No new dependencies added. Uses existing:
- `dataclasses.dataclass`
- Standard Python typing
- Existing Grade enum
