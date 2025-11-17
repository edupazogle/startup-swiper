/* eslint-disable jsx-a11y/anchor-is-valid */
import type { FC } from "react";
import { useState } from "react";
import NavbarSidebarLayout from "../layouts/navbar-sidebar";

const CalendarPage: FC = function () {
  const [selectedView, setSelectedView] = useState<"month" | "week" | "day">("month");
  const [selectedDate, setSelectedDate] = useState(new Date());

  return (
    <NavbarSidebarLayout>
      <div className="px-4 pt-6">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
            Calendar
          </h1>
        </div>

        <div className="grid gap-6 xl:grid-cols-4">
          {/* Main Calendar Area */}
          <div className="xl:col-span-3">
            <CalendarWidget 
              selectedView={selectedView}
              setSelectedView={setSelectedView}
              selectedDate={selectedDate}
              setSelectedDate={setSelectedDate}
            />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <UpcomingEvents />
            <EventCategories />
          </div>
        </div>
      </div>
    </NavbarSidebarLayout>
  );
};

const CalendarWidget: FC<{
  selectedView: "month" | "week" | "day";
  setSelectedView: (view: "month" | "week" | "day") => void;
  selectedDate: Date;
  setSelectedDate: (date: Date) => void;
}> = function ({ selectedView, setSelectedView, selectedDate, setSelectedDate }) {
  const monthNames = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"];

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    return { daysInMonth, startingDayOfWeek };
  };

  const { daysInMonth, startingDayOfWeek } = getDaysInMonth(selectedDate);

  const handlePrevMonth = () => {
    setSelectedDate(new Date(selectedDate.getFullYear(), selectedDate.getMonth() - 1));
  };

  const handleNextMonth = () => {
    setSelectedDate(new Date(selectedDate.getFullYear(), selectedDate.getMonth() + 1));
  };

  const handleToday = () => {
    setSelectedDate(new Date());
  };

  // Sample events data
  const events = [
    { date: 8, title: "Team Meeting", type: "business", time: "10:00 AM" },
    { date: 15, title: "Investor Pitch", type: "important", time: "2:00 PM" },
    { date: 22, title: "Product Demo", type: "demo", time: "11:30 AM" },
    { date: 28, title: "Quarterly Review", type: "meetup", time: "3:00 PM" },
  ];

  return (
    <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
      {/* Calendar Header */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {monthNames[selectedDate.getMonth()]} {selectedDate.getFullYear()}
          </h2>
          <button
            onClick={handleToday}
            className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
          >
            Today
          </button>
        </div>

        <div className="flex items-center gap-3">
          {/* View Selector */}
          <div className="inline-flex rounded-lg border border-gray-300 dark:border-gray-600">
            <button
              onClick={() => setSelectedView("month")}
              className={`rounded-l-lg px-3 py-1.5 text-sm font-medium ${
                selectedView === "month"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-700 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
              }`}
            >
              Month
            </button>
            <button
              onClick={() => setSelectedView("week")}
              className={`border-x border-gray-300 px-3 py-1.5 text-sm font-medium dark:border-gray-600 ${
                selectedView === "week"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-700 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
              }`}
            >
              Week
            </button>
            <button
              onClick={() => setSelectedView("day")}
              className={`rounded-r-lg px-3 py-1.5 text-sm font-medium ${
                selectedView === "day"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-700 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
              }`}
            >
              Day
            </button>
          </div>

          {/* Navigation Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrevMonth}
              className="rounded-lg border border-gray-300 bg-white p-2 text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
              aria-label="Previous month"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button
              onClick={handleNextMonth}
              className="rounded-lg border border-gray-300 bg-white p-2 text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
              aria-label="Next month"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700">
        {/* Day Headers */}
        <div className="grid grid-cols-7 border-b border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-700">
          {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
            <div
              key={day}
              className="border-r border-gray-200 px-3 py-3 text-center text-sm font-semibold text-gray-700 last:border-r-0 dark:border-gray-700 dark:text-gray-300"
            >
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Days */}
        <div className="grid grid-cols-7 bg-white dark:bg-gray-800">
          {/* Empty cells for days before month starts */}
          {Array.from({ length: startingDayOfWeek }).map((_, index) => (
            <div
              key={`empty-${index}`}
              className="min-h-[120px] border-b border-r border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900 last:border-r-0"
            />
          ))}

          {/* Days of the month */}
          {Array.from({ length: daysInMonth }).map((_, index) => {
            const dayNumber = index + 1;
            const dayEvents = events.filter((e) => e.date === dayNumber);
            const isToday = 
              dayNumber === new Date().getDate() &&
              selectedDate.getMonth() === new Date().getMonth() &&
              selectedDate.getFullYear() === new Date().getFullYear();

            return (
              <div
                key={dayNumber}
                className={`group min-h-[120px] border-b border-r border-gray-200 p-2 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-700 last:border-r-0 ${
                  isToday ? "bg-blue-50 dark:bg-blue-900/20" : ""
                }`}
              >
                <div className="mb-2 flex items-center justify-between">
                  <span
                    className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-sm font-medium ${
                      isToday
                        ? "bg-blue-600 text-white"
                        : "text-gray-700 dark:text-gray-300"
                    }`}
                  >
                    {dayNumber}
                  </span>
                  <button
                    className="hidden rounded p-1 text-gray-400 hover:bg-gray-200 hover:text-gray-600 group-hover:block dark:hover:bg-gray-600 dark:hover:text-gray-300"
                    aria-label="Add event"
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  </button>
                </div>

                {/* Events for this day */}
                <div className="space-y-1">
                  {dayEvents.map((event, eventIndex) => (
                    <div
                      key={eventIndex}
                      className={`cursor-pointer rounded px-2 py-1 text-xs font-medium truncate ${
                        event.type === "business"
                          ? "bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-900/30 dark:text-blue-400"
                          : event.type === "important"
                          ? "bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400"
                          : event.type === "demo"
                          ? "bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400"
                          : "bg-purple-100 text-purple-700 hover:bg-purple-200 dark:bg-purple-900/30 dark:text-purple-400"
                      }`}
                      title={`${event.time} - ${event.title}`}
                    >
                      {event.title}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const UpcomingEvents: FC = function () {
  const upcomingEvents = [
    {
      id: 1,
      title: "Team Meeting",
      date: "Jul 8",
      time: "10:00-11:00 AM",
      type: "business",
      avatar: "https://cdn.flyonui.com/fy-assets/avatar/avatar-1.png",
    },
    {
      id: 2,
      title: "Investor Pitch",
      date: "Jul 15",
      time: "2:00-3:30 PM",
      type: "important",
      avatar: "https://cdn.flyonui.com/fy-assets/avatar/avatar-2.png",
    },
    {
      id: 3,
      title: "Product Demo",
      date: "Jul 22",
      time: "11:30 AM-12:30 PM",
      type: "demo",
      avatar: "https://cdn.flyonui.com/fy-assets/avatar/avatar-3.png",
    },
    {
      id: 4,
      title: "Quarterly Review",
      date: "Jul 28",
      time: "3:00-4:00 PM",
      type: "meetup",
      avatar: "https://cdn.flyonui.com/fy-assets/avatar/avatar-4.png",
    },
  ];

  const getBadgeColor = (type: string) => {
    switch (type) {
      case "business":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
      case "important":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300";
      case "demo":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300";
      case "meetup":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300";
    }
  };

  return (
    <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Upcoming Events
        </h3>
        <button className="text-blue-600 hover:text-blue-700 dark:text-blue-500">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </button>
      </div>

      <ul className="space-y-4">
        {upcomingEvents.map((event) => (
          <li key={event.id}>
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0">
                <img
                  className="h-10 w-10 rounded-full"
                  src={event.avatar}
                  alt={event.title}
                />
              </div>
              <div className="min-w-0 flex-1">
                <h4 className="mb-1 font-medium text-gray-900 dark:text-white">
                  {event.title}
                </h4>
                <div className="mb-2 flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span>{event.date} | {event.time}</span>
                </div>
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getBadgeColor(event.type)}`}>
                  {event.type.charAt(0).toUpperCase() + event.type.slice(1)}
                </span>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

const EventCategories: FC = function () {
  const categories = [
    { name: "Business", count: 12, color: "bg-blue-600" },
    { name: "Important", count: 8, color: "bg-red-600" },
    { name: "Demo", count: 5, color: "bg-green-600" },
    { name: "Meetup", count: 15, color: "bg-purple-600" },
  ];

  return (
    <div className="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
      <h3 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
        Event Categories
      </h3>
      <ul className="space-y-3">
        {categories.map((category) => (
          <li key={category.name}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`h-3 w-3 rounded-full ${category.color}`} />
                <span className="text-gray-700 dark:text-gray-300">
                  {category.name}
                </span>
              </div>
              <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-300">
                {category.count}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CalendarPage;
