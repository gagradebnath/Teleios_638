import React, { useState, useEffect } from 'react';
import { gateway } from '../api/gateway';
import './CourseSelector.css';

const CourseSelector = ({ onCourseSelect, selectedCourseId }) => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showNewCourseModal, setShowNewCourseModal] = useState(false);
    const [newCourse, setNewCourse] = useState({
        name: '',
        code: '',
        description: '',
        color: '#3b82f6',
    });

    // Load courses
    const loadCourses = async () => {
        setLoading(true);
        try {
            const fetchedCourses = await gateway.listCourses();
            setCourses(fetchedCourses || []);
        } catch (err) {
            console.error('Error loading courses:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadCourses();
    }, []);

    // Create new course
    const handleCreateCourse = async () => {
        if (!newCourse.name.trim()) {
            alert('Please enter a course name');
            return;
        }

        try {
            const created = await gateway.createCourse(newCourse);
            setNewCourse({ name: '', code: '', description: '', color: '#3b82f6' });
            setShowNewCourseModal(false);
            loadCourses(); // Refresh
            onCourseSelect?.(created);
        } catch (err) {
            alert(`Error creating course: ${err.message}`);
        }
    };

    // Predefined colors
    const colors = [
        '#3b82f6', // blue
        '#10b981', // green
        '#f59e0b', // amber
        '#ef4444', // red
        '#8b5cf6', // purple
        '#ec4899', // pink
        '#06b6d4', // cyan
        '#84cc16', // lime
    ];

    return (
        <div className="course-selector">
            <div className="course-selector-header">
                <h5>Courses</h5>
                <button
                    className="btn btn-primary btn-sm"
                    onClick={() => setShowNewCourseModal(true)}
                    title="Add new course"
                >
                    ➕
                </button>
            </div>

            {loading && <div className="loading">Loading courses...</div>}

            <div className="course-list">
                {/* All Courses option */}
                <div
                    className={`course-item ${!selectedCourseId ? 'active' : ''}`}
                    onClick={() => onCourseSelect?.(null)}
                >
                    <div
                        className="course-color"
                        style={{ background: '#6c757d' }}
                    />
                    <div className="course-info">
                        <div className="course-name">All Courses</div>
                        <div className="course-code">View all materials</div>
                    </div>
                </div>

                {/* Course items */}
                {courses.map((course) => (
                    <div
                        key={course.id}
                        className={`course-item ${selectedCourseId === course.id ? 'active' : ''}`}
                        onClick={() => onCourseSelect?.(course)}
                    >
                        <div
                            className="course-color"
                            style={{ background: course.color || '#3b82f6' }}
                        />
                        <div className="course-info">
                            <div className="course-name">{course.name}</div>
                            {course.code && (
                                <div className="course-code">{course.code}</div>
                            )}
                        </div>
                    </div>
                ))}

                {courses.length === 0 && !loading && (
                    <div className="empty-state">
                        No courses yet. Click ➕ to create one.
                    </div>
                )}
            </div>

            {/* New Course Modal */}
            {showNewCourseModal && (
                <div
                    className="modal-overlay"
                    onClick={() => setShowNewCourseModal(false)}
                >
                    <div
                        className="modal-content"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h3>Create New Course</h3>

                        <div className="form-group">
                            <label>Course Name *</label>
                            <input
                                type="text"
                                className="form-control"
                                placeholder="e.g., Calculus I"
                                value={newCourse.name}
                                onChange={(e) =>
                                    setNewCourse({ ...newCourse, name: e.target.value })
                                }
                                autoFocus
                            />
                        </div>

                        <div className="form-group">
                            <label>Course Code</label>
                            <input
                                type="text"
                                className="form-control"
                                placeholder="e.g., MATH101"
                                value={newCourse.code}
                                onChange={(e) =>
                                    setNewCourse({ ...newCourse, code: e.target.value })
                                }
                            />
                        </div>

                        <div className="form-group">
                            <label>Description</label>
                            <textarea
                                className="form-control"
                                placeholder="Optional description"
                                rows="3"
                                value={newCourse.description}
                                onChange={(e) =>
                                    setNewCourse({
                                        ...newCourse,
                                        description: e.target.value,
                                    })
                                }
                            />
                        </div>

                        <div className="form-group">
                            <label>Color</label>
                            <div className="color-picker">
                                {colors.map((color) => (
                                    <button
                                        key={color}
                                        className={`color-option ${
                                            newCourse.color === color ? 'active' : ''
                                        }`}
                                        style={{ background: color }}
                                        onClick={() =>
                                            setNewCourse({ ...newCourse, color })
                                        }
                                        title={color}
                                    />
                                ))}
                            </div>
                        </div>

                        <div className="modal-actions">
                            <button
                                className="btn btn-secondary"
                                onClick={() => setShowNewCourseModal(false)}
                            >
                                Cancel
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={handleCreateCourse}
                            >
                                Create Course
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CourseSelector;
