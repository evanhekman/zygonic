
import React from 'react';
import { Todo } from '../types';
import { TodoItem } from './TodoItem';

interface TodoListProps {
  todos: Todo[];
  onUpdateProgress: (id: string, progress: number) => void;
  onDeleteTodo: (id: string) => void;
  onUpdateText: (id: string, text: string) => void;
}

export const TodoList: React.FC<TodoListProps> = ({ todos, onUpdateProgress, onDeleteTodo, onUpdateText }) => {
  if (todos.length === 0) {
    return (
      <div className="text-center py-10 px-4 bg-slate-800/50 rounded-xl border border-slate-700">
        <p className="text-slate-400 text-lg">Your task list is empty.</p>
        <p className="text-slate-500 text-sm mt-1">Add a new task above to get started!</p>
      </div>
    );
  }

  const sortedTodos = [...todos].sort((a, b) => a.createdAt - b.createdAt);
  
  return (
    <div className="space-y-4">
      {sortedTodos.map(todo => (
        <TodoItem 
          key={todo.id} 
          todo={todo}
          onUpdateProgress={onUpdateProgress}
          onDeleteTodo={onDeleteTodo}
          onUpdateText={onUpdateText}
        />
      ))}
    </div>
  );
};
