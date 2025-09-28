import React, { useState, useRef, useEffect } from 'react';
import { Task } from '../types';
import { TrashIcon } from './Icons';

interface TodoItemProps {
  task: Task;
  onUpdateProgress: (id: number, progress: number) => void;
  onDeleteTask: (id: number) => void;
  onUpdateText: (id: number, description: string) => void;
  onStartTask?: (id: number) => void;
  onRefreshTasks?: () => void;
}

export const TodoItem: React.FC<TodoItemProps> = ({ task, onUpdateProgress, onDeleteTask, onUpdateText, onStartTask, onRefreshTasks }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(task.description);
  const inputRef = useRef<HTMLInputElement>(null);
  const [localProgress, setLocalProgress] = useState(Math.round(task.progress * 100));
  const [isStarting, setIsStarting] = useState(false);

  useEffect(() => {
    if (isEditing) {
      inputRef.current?.focus();
    }
  }, [isEditing]);

  useEffect(() => {
    setLocalProgress(Math.round(task.progress * 100));
  }, [task.progress]);

  const handleProgressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newProgress = parseInt(e.target.value, 10);
    setLocalProgress(newProgress);
    // Update immediately during drag for real-time feedback
    const progressAsDecimal = newProgress / 100;
    onUpdateProgress(task.id, progressAsDecimal);
  };

  const handleProgressComplete = () => {
    // This is now just for any final cleanup if needed
    // The actual update happens in handleProgressChange
  };

  const handleStartTask = async () => {
    if (onStartTask) {
      setIsStarting(true);
      try {
        await onStartTask(task.id);
        // Trigger data refresh after successful start
        if (onRefreshTasks) {
          onRefreshTasks();
        }
      } catch (error) {
        console.error('Failed to start task:', error);
      } finally {
        setIsStarting(false);
      }
    }
  };

  const handleTextUpdate = () => {
    if (editText.trim() && editText.trim() !== task.description) {
      onUpdateText(task.id, editText.trim());
    } else {
      setEditText(task.description);
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleTextUpdate();
    } else if (e.key === 'Escape') {
      setEditText(task.description);
      setIsEditing(false);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return '';
    }
  };

  return (
    <div className={`p-6 bg-slate-800 rounded-lg shadow-lg flex flex-col gap-4 border border-slate-700 transition-all duration-300 hover:border-slate-600 hover:bg-slate-700/50 ${localProgress === 100 ? 'opacity-60' : ''}`}>
      <div className="flex justify-between items-start gap-4">
        {isEditing ? (
          <input
            ref={inputRef}
            type="text"
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            onBlur={handleTextUpdate}
            onKeyDown={handleKeyDown}
            className="flex-grow bg-slate-700 text-slate-100 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500 w-full"
          />
        ) : (
          <div className="flex-grow min-w-0">
            <p 
              className={`text-lg text-slate-200 break-words cursor-pointer leading-relaxed ${localProgress === 100 ? 'line-through text-slate-400' : ''}`}
              onDoubleClick={() => setIsEditing(true)}
              title="Double-click to edit"
            >
              {task.description}
            </p>
            <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <span className={`w-2 h-2 rounded-full ${
                  localProgress === 100 ? 'bg-green-500' : 
                  localProgress > 0 ? 'bg-cyan-500' : 'bg-slate-500'
                }`}></span>
                {task.status}
              </span>
              <span>Created: {formatDate(task.created_at)}</span>
            </div>
          </div>
        )}
        <button 
          onClick={() => onDeleteTask(task.id)} 
          className="text-slate-500 hover:text-red-500 transition-colors duration-200 flex-shrink-0 p-1 rounded hover:bg-slate-700"
          aria-label="Delete task"
        >
          <TrashIcon className="w-5 h-5" />
        </button>
      </div>

      {/* Progress Section with proper alignment */}
      <div className="flex items-center gap-4">
        <div className="flex-grow relative">
          {/* Background track for the slider */}
          <div className="absolute inset-0 top-1/3 bg-slate-600 rounded-full h-2 pointer-events-none" />
          {/* Progress fill that matches the slider position */}
          <div 
            className={`absolute left-0 top-1/3 h-2 rounded-full transition-all duration-150 pointer-events-none ${
              localProgress === 100 ? 'bg-green-500' : 'bg-cyan-500'
            }`}
            style={{ width: `${localProgress}%` }}
          />
          
          {/* Start button overlay when progress is 0% */}
          {localProgress === 0 && onStartTask && (
            <button
              onClick={handleStartTask}
              disabled={isStarting}
              className={`absolute inset-0 text-white text-sm font-medium rounded-lg transition-all duration-200 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl z-30 ${
                isStarting 
                  ? 'bg-cyan-500 cursor-not-allowed' 
                  : 'bg-cyan-600 hover:bg-cyan-700'
              }`}
            >
              {isStarting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Starting...
                </>
              ) : (
                'Start Task'
              )}
            </button>
          )}
          
          <input
            type="range"
            min="0"
            max="100"
            step="1"
            value={localProgress}
            onChange={handleProgressChange}
            onMouseUp={handleProgressComplete}
            onTouchEnd={handleProgressComplete}
            className={`w-full range-slider cursor-pointer relative z-10`}
            style={{ background: 'transparent' }}
          />
        </div>
        <div className="flex-shrink-0 flex items-center gap-2">
          <span className={`text-sm font-bold tabular-nums w-12 text-right ${
            localProgress === 100 ? 'text-green-400' : 'text-cyan-400'
          }`}>
            {localProgress}%
          </span>
        </div>
      </div>
    </div>
  );
};