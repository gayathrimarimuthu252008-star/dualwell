import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import {
  Calendar as CalendarIcon,
  Plus,
  Download,
  AlertTriangle,
  Clock,
  Trash2,
  CheckCircle,
  Filter,
  CheckSquare,
  Square
} from 'lucide-react';

export const AcademicCalendarPage: React.FC = () => {
  const [events, setEvents] = useState<any[]>([]);
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [filterType, setFilterType] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'agenda' | 'calendar'>('agenda');

  // Form state
  const [title, setTitle] = useState('');
  const [eventType, setEventType] = useState('exam');
  const [courseName, setCourseName] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [priority, setPriority] = useState('high');
  const [workloadHours, setWorkloadHours] = useState(2.5);
  const [isFixed, setIsFixed] = useState(true);
  const [notes, setNotes] = useState('');

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const [eventsRes, conflictsRes] = await Promise.all([
        apiClient.get('/academic/events'),
        apiClient.get('/academic/conflicts')
      ]);
      setEvents(eventsRes.data || []);
      setConflicts(conflictsRes.data.conflicts || []);
    } catch (err) {
      console.error('Error fetching calendar data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleCreateEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/academic/events', {
        title,
        event_type: eventType,
        course_name: courseName || null,
        start_time: new Date(startTime).toISOString(),
        end_time: new Date(endTime).toISOString(),
        priority,
        estimated_workload_hours: Number(workloadHours),
        is_fixed: isFixed,
        is_completed: false,
        notes: notes || null,
      });

      setShowAddModal(false);
      // Reset form
      setTitle('');
      setCourseName('');
      setStartTime('');
      setEndTime('');
      setNotes('');
      await fetchEvents();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create academic event.');
    }
  };

  const handleDeleteEvent = async (id: number) => {
    if (!confirm('Are you sure you want to remove this academic event?')) return;
    try {
      await apiClient.delete(`/academic/events/${id}`);
      await fetchEvents();
    } catch (err) {
      console.error('Failed to delete event:', err);
    }
  };

  const handleToggleComplete = async (event: any) => {
    try {
      await apiClient.put(`/academic/events/${event.id}`, {
        is_completed: !event.is_completed,
      });
      await fetchEvents();
    } catch (err) {
      console.error('Failed to update event:', err);
    }
  };

  const handleExportICS = async () => {
    try {
      const res = await apiClient.get('/academic/export-ics', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'dualwell_academic_calendar.ics');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('ICS Export failed:', err);
    }
  };

  const filteredEvents = events.filter((ev) => {
    if (filterType === 'all') return true;
    return ev.event_type === filterType;
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-dualtext-primary">
            Academic Calendar & Workload Manager
          </h2>
          <p className="text-xs sm:text-sm text-dualtext-secondary">
            Coordinate coursework, exams, and study commitments alongside athletic training.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleExportICS}
            className="flex items-center space-x-1.5 bg-white border border-bordercolor hover:border-primary text-dualtext-primary hover:text-primary px-3 py-2 rounded-xl text-xs font-semibold shadow-xs transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export .ICS</span>
          </button>

          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center space-x-1.5 bg-primary hover:bg-primary-hover text-white px-3.5 py-2 rounded-xl text-xs font-semibold shadow-xs transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Event</span>
          </button>
        </div>
      </div>

      {/* Conflict Warning Alerts if detected */}
      {conflicts.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 space-y-2">
          <div className="flex items-center space-x-2 text-risk-yellow font-bold text-xs sm:text-sm">
            <AlertTriangle className="w-4 h-4" />
            <span>Schedule Conflict Warning: {conflicts.length} Overload or Clash Issues Detected</span>
          </div>
          <div className="space-y-1.5 pl-6">
            {conflicts.map((cf, idx) => (
              <p key={idx} className="text-xs text-dualtext-secondary leading-relaxed">
                • <strong className="text-dualtext-primary">{cf.title}:</strong> {cf.description}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Filter and View mode switcher */}
      <div className="bg-white rounded-2xl border border-bordercolor p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs font-semibold text-dualtext-secondary mr-2 flex items-center space-x-1">
            <Filter className="w-3.5 h-3.5" />
            <span>Filter:</span>
          </span>
          {['all', 'exam', 'deadline', 'assignment', 'class', 'study_session'].map((ft) => (
            <button
              key={ft}
              onClick={() => setFilterType(ft)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold capitalize transition-all ${
                filterType === ft
                  ? 'bg-primary text-white shadow-xs'
                  : 'bg-dualbg text-dualtext-secondary hover:text-dualtext-primary'
              }`}
            >
              {ft.replace('_', ' ')}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-1 bg-dualbg p-1 rounded-xl self-start sm:self-auto">
          <button
            onClick={() => setViewMode('agenda')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold ${
              viewMode === 'agenda' ? 'bg-white text-primary shadow-xs' : 'text-dualtext-secondary'
            }`}
          >
            Agenda View
          </button>
          <button
            onClick={() => setViewMode('calendar')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold ${
              viewMode === 'calendar' ? 'bg-white text-primary shadow-xs' : 'text-dualtext-secondary'
            }`}
          >
            Grid View
          </button>
        </div>
      </div>

      {/* Events List / Agenda */}
      {loading ? (
        <div className="flex justify-center p-12">
          <div className="w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
        </div>
      ) : filteredEvents.length === 0 ? (
        <div className="bg-white rounded-2xl border border-bordercolor p-12 text-center shadow-xs">
          <CalendarIcon className="w-10 h-10 text-dualtext-secondary mx-auto mb-3 opacity-40" />
          <h3 className="text-sm font-bold text-dualtext-primary">No Academic Events Found</h3>
          <p className="text-xs text-dualtext-secondary mt-1">
            Add upcoming exams, assignments, or study sessions to evaluate your dual-load.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredEvents.map((ev) => {
            const startD = new Date(ev.start_time);
            const endD = new Date(ev.end_time);
            return (
              <div
                key={ev.id}
                className={`bg-white rounded-2xl border p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 transition-all ${
                  ev.is_completed
                    ? 'border-bordercolor opacity-60 bg-gray-50/50'
                    : ev.priority === 'critical'
                    ? 'border-risk-red/30 shadow-xs'
                    : 'border-bordercolor hover:border-primary/40 shadow-xs'
                }`}
              >
                <div className="flex items-start space-x-3.5">
                  <button
                    onClick={() => handleToggleComplete(ev)}
                    className="mt-1 text-dualtext-secondary hover:text-primary transition-colors"
                  >
                    {ev.is_completed ? (
                      <CheckSquare className="w-5 h-5 text-risk-green" />
                    ) : (
                      <Square className="w-5 h-5" />
                    )}
                  </button>

                  <div>
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                          ev.event_type === 'exam'
                            ? 'bg-red-50 text-risk-red border border-red-200'
                            : ev.event_type === 'deadline'
                            ? 'bg-amber-50 text-risk-yellow border border-amber-200'
                            : 'bg-primary-soft text-primary border border-primary/20'
                        }`}
                      >
                        {ev.event_type.replace('_', ' ')}
                      </span>
                      {ev.course_name && (
                        <span className="text-[10px] bg-dualbg font-semibold text-dualtext-secondary px-2 py-0.5 rounded">
                          {ev.course_name}
                        </span>
                      )}
                      <span
                        className={`text-[10px] font-semibold ${
                          ev.priority === 'critical'
                            ? 'text-risk-red font-bold'
                            : 'text-dualtext-secondary'
                        }`}
                      >
                        Priority: {ev.priority}
                      </span>
                    </div>

                    <h3
                      className={`text-sm sm:text-base font-bold ${
                        ev.is_completed ? 'line-through text-dualtext-secondary' : 'text-dualtext-primary'
                      }`}
                    >
                      {ev.title}
                    </h3>

                    <div className="flex flex-wrap items-center gap-3 text-xs text-dualtext-secondary mt-1">
                      <span className="flex items-center space-x-1">
                        <Clock className="w-3.5 h-3.5" />
                        <span>
                          {startD.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} •{' '}
                          {startD.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} –{' '}
                          {endD.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </span>
                      <span>•</span>
                      <span>Est. Workload: {ev.estimated_workload_hours}h</span>
                      <span>•</span>
                      <span>{ev.is_fixed ? 'Fixed Schedule' : 'Flexible (Can move)'}</span>
                    </div>

                    {ev.notes && (
                      <p className="text-xs text-dualtext-secondary mt-2 italic bg-dualbg p-2 rounded-lg">
                        {ev.notes}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2 self-end sm:self-center">
                  <button
                    onClick={() => handleDeleteEvent(ev.id)}
                    className="p-2 text-dualtext-secondary hover:text-risk-red hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete Event"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add Event Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/30 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 border border-bordercolor shadow-xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4 border-b border-bordercolor pb-3">
              <h3 className="text-base font-bold text-dualtext-primary">
                Add Academic Commitment
              </h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-dualtext-secondary hover:text-dualtext-primary text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateEvent} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-dualtext-primary mb-1">
                  Event Title *
                </label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Operating Systems Midterm Exam"
                  className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-dualtext-primary mb-1">
                    Event Type
                  </label>
                  <select
                    value={eventType}
                    onChange={(e) => setEventType(e.target.value)}
                    className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary bg-white"
                  >
                    <option value="exam">Exam</option>
                    <option value="deadline">Deadline</option>
                    <option value="assignment">Assignment</option>
                    <option value="class">Class / Lecture</option>
                    <option value="study_session">Study Session</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-dualtext-primary mb-1">
                    Course Code / Name
                  </label>
                  <input
                    type="text"
                    value={courseName}
                    onChange={(e) => setCourseName(e.target.value)}
                    placeholder="e.g. CS 301"
                    className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-dualtext-primary mb-1">
                    Start Time *
                  </label>
                  <input
                    type="datetime-local"
                    required
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-dualtext-primary mb-1">
                    End Time *
                  </label>
                  <input
                    type="datetime-local"
                    required
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-dualtext-primary mb-1">
                    Priority Tier
                  </label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary bg-white"
                  >
                    <option value="critical">Critical (Exams, Finals)</option>
                    <option value="high">High (Major Deliverables)</option>
                    <option value="medium">Medium (Regular Study)</option>
                    <option value="low">Low (Optional Reading)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-dualtext-primary mb-1">
                    Est. Workload Hours
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    min="0.5"
                    max="12"
                    value={workloadHours}
                    onChange={(e) => setWorkloadHours(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2 pt-1">
                <input
                  type="checkbox"
                  id="isFixed"
                  checked={isFixed}
                  onChange={(e) => setIsFixed(e.target.checked)}
                  className="rounded text-primary focus:ring-primary"
                />
                <label htmlFor="isFixed" className="text-xs text-dualtext-primary">
                  Fixed Event (Cannot be automatically moved by Smart Scheduler)
                </label>
              </div>

              <div>
                <label className="block text-xs font-medium text-dualtext-primary mb-1">
                  Notes or Syllabus Focus
                </label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Key topics, exam room location, or materials to bring..."
                  className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="flex space-x-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 py-2 border border-bordercolor text-dualtext-secondary text-xs font-semibold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-xl shadow-xs"
                >
                  Save Academic Event
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
