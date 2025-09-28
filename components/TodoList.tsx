import React from 'react';
import { Task } from '../types';
import { TodoItem } from './TodoItem';

interface TodoListProps {
  tasks: Task[];
  onUpdateProgress: (id: number, progress: number) => void;
  onDeleteTask: (id: number) => void;
  onUpdateText: (id: number, description: string) => void;
  onStartTask?: (id: number) => void;
  onRefreshTasks?: () => void;
}

export const TodoList: React.FC<TodoListProps> = ({ 
  tasks, 
  onUpdateProgress, 
  onDeleteTask, 
  onUpdateText, 
  onStartTask,
  onRefreshTasks
}) => {
  if (tasks.length === 0) {
    return (
      <div className="text-center py-10 px-4 bg-slate-800/50 rounded-xl border border-slate-700">
        <p className="text-slate-400 text-lg">Your task list is empty.</p>
        <p className="text-slate-500 text-sm mt-1">Add a new task above to get started!</p>
      </div>
    );
  }

  const handleStartTask = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/start?task_id=${id}`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to start task');
      // Handle success - maybe refetch tasks
    } catch (error) {
      console.error('Error starting task:', error);
    }
  };

  // Sort by created_at timestamp, newest first
  const sortedTasks = [...tasks].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
  
  return (
    <div className="space-y-4">
      {sortedTasks.map(task => (
        <TodoItem 
          key={task.id} 
          task={task}
          onUpdateProgress={onUpdateProgress}
          onDeleteTask={onDeleteTask}
          onUpdateText={onUpdateText}
          onStartTask={handleStartTask}
          onRefreshTasks={onRefreshTasks}
        />
      ))}
    </div>
  );
};