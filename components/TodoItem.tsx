import React, { useState, useRef, useEffect } from 'react';
import { Todo } from '../types';
import { TrashIcon } from './Icons';

interface TodoItemProps {
  todo: Todo;
  onUpdateProgress: (id: string, progress: number) => void;
  onDeleteTodo: (id: string) => void;
  onUpdateText: (id: string, text: string) => void;
}

export const TodoItem: React.FC<TodoItemProps> = ({ todo, onUpdateProgress, onDeleteTodo, onUpdateText }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(todo.text);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing) {
      inputRef.current?.focus();
    }
  }, [isEditing]);
  
  const handleTextUpdate = () => {
    if (editText.trim() && editText.trim() !== todo.text) {
      onUpdateText(todo.id, editText.trim());
    } else {
      setEditText(todo.text);
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleTextUpdate();
    } else if (e.key === 'Escape') {
      setEditText(todo.text);
      setIsEditing(false);
    }
  };

  const sliderStyle = {
    background: `linear-gradient(to right, ${todo.progress === 100 ? '#10b981' : '#06b6d4'} ${todo.progress}%, #475569 ${todo.progress}%)`
  };

  return (
    <div className={`p-4 bg-slate-800 rounded-lg shadow-lg flex flex-col gap-4 border border-slate-700 transition-all duration-300 hover:border-slate-600 hover:bg-slate-700/50 ${todo.progress === 100 ? 'opacity-60' : ''}`}>
      <div className="flex justify-between items-start gap-4">
        {isEditing ? (
          <input
            ref={inputRef}
            type="text"
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            onBlur={handleTextUpdate}
            onKeyDown={handleKeyDown}
            className="flex-grow bg-slate-700 text-slate-100 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-cyan-500 w-full"
          />
        ) : (
          <p 
            className={`flex-grow text-lg text-slate-200 break-words cursor-pointer ${todo.progress === 100 ? 'line-through text-slate-400' : ''}`}
            onDoubleClick={() => setIsEditing(true)}
          >
            {todo.text}
          </p>
        )}
        <button 
          onClick={() => onDeleteTodo(todo.id)} 
          className="text-slate-500 hover:text-red-500 transition-colors duration-200 flex-shrink-0"
          aria-label="Delete task"
        >
          <TrashIcon className="w-5 h-5" />
        </button>
      </div>

      {todo.isLoadingNextSteps && (
        <div className="mt-2 flex items-center gap-2 text-sm text-slate-400">
          <div className="w-4 h-4 border-2 border-slate-600 border-t-cyan-400 rounded-full animate-spin"></div>
          <span>Generating next steps...</span>
        </div>
      )}

      {!todo.isLoadingNextSteps && todo.nextSteps && todo.nextSteps.length > 0 && (
        <div className="mt-3 pt-3 border-t border-slate-700/50">
          <h4 className="text-sm font-semibold text-slate-300 mb-2">Suggested Next Steps:</h4>
          <ul className="list-disc list-inside space-y-1.5 pl-1">
            {todo.nextSteps.map((step, index) => (
              <li key={index} className="text-slate-400 text-sm">
                {step}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex items-center gap-4 pt-2">
        <input
          type="range"
          min="0"
          max="100"
          value={todo.progress}
          onChange={(e) => onUpdateProgress(todo.id, parseInt(e.target.value, 10))}
          className="w-full h-1.5 rounded-lg appearance-none cursor-pointer"
          style={sliderStyle}
        />
        <span className="text-sm font-semibold text-cyan-400 w-12 text-right">{todo.progress}%</span>
      </div>
    </div>
  );
};