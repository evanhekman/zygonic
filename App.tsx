import React, { useState, useEffect } from 'react';
import { Task } from './types';
import { AddTodoForm } from './components/AddTodoForm';
import { TodoList } from './components/TodoList';
import { GlobalStyles } from './Styles';
import { apiService } from './api';

const App: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch all tasks on component mount
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        setError(null);
        const fetchedTasks = await apiService.getAllTasks();
        setTasks(fetchedTasks);
      } catch (err) {
        setError('Failed to load tasks. Please check if the server is running.');
        console.error('Error fetching tasks:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  const addTask = async (description: string) => {
    // Create optimistic task with temporary ID
    const tempTask: Task = {
      id: Date.now(), // Temporary ID
      description,
      action: {},
      status: 'NEW',
      progress: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    // Optimistic update - add to UI immediately
    setTasks(prevTasks => [tempTask, ...prevTasks]);

    try {
      setError(null);
      const realTaskId = await apiService.createTask(description, 'NEW', 0);
      
      // Replace with real data from backend
      const updatedTasks = await apiService.getAllTasks();
      setTasks(updatedTasks);
    } catch (err) {
      // Remove temp task on error
      setTasks(prevTasks => prevTasks.filter(task => task.id !== tempTask.id));
      setError('Failed to create task.');
      console.error('Error creating task:', err);
    }
  };

  const deleteTask = async (id: number) => {
    // Store task for potential rollback
    const taskToDelete = tasks.find(t => t.id === id);
    
    // Optimistic update - remove from UI immediately
    setTasks(prevTasks => prevTasks.filter(task => task.id !== id));

    try {
      setError(null);
      await apiService.deleteTask(id);
    } catch (err) {
      // Revert on error
      if (taskToDelete) {
        setTasks(prevTasks => [...prevTasks, taskToDelete].sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        ));
      }
      setError('Failed to delete task.');
      console.error('Error deleting task:', err);
    }
  };
  
  const updateTaskDescription = async (id: number, description: string) => {
    // Store original for potential rollback
    const originalTask = tasks.find(t => t.id === id);
    
    // Optimistic update
    setTasks(prevTasks => 
      prevTasks.map(task => 
        task.id === id ? { ...task, description } : task
      )
    );

    try {
      setError(null);
      await apiService.updateTask(id, { description, status: 'NEW', progress: 0 });
    } catch (err) {
      // Revert on error
      if (originalTask) {
        setTasks(prevTasks => 
          prevTasks.map(task => 
            task.id === id ? originalTask : task
          )
        );
      }
      setError('Failed to update task.');
      console.error('Error updating task:', err);
    }
  };

  const updateTaskProgress = async (id: number, progress: number) => {
    // progress is already 0-1 from the slider (e.g., 0.36)
    const status = Math.round(progress * 100) === 100 ? 'COMPLETED' : progress > 0 ? 'STARTED' : 'NEW';
    
    // Store original for potential rollback
    const originalTask = tasks.find(t => t.id === id);
    
    // Store as decimal to match backend format
    setTasks(prevTasks => 
      prevTasks.map(task => 
        task.id === id ? { ...task, progress, status } : task  // Store 0.36, not 36
      )
    );

    try {
      setError(null);
      const description = tasks.find(t => t.id === id)?.description || '';
      await apiService.updateTask(id, { progress, status, description });
    } catch (err) {
      if (originalTask) {
        setTasks(prevTasks => 
          prevTasks.map(task => 
            task.id === id ? originalTask : task
          )
        );
      }
      setError('Failed to update progress.');
      console.error('Error updating progress:', err);
    }
  };  

  const completedCount = tasks.filter(t => t.progress === 100).length;
  const totalCount = tasks.length;
  const overallProgress = totalCount > 0 ? Math.round(tasks.reduce((sum, task) => sum + task.progress, 0) / totalCount) : 0;

  if (loading) {
    return (
      <div className="bg-slate-900 text-white min-h-screen font-sans flex flex-col items-center justify-center">
        <GlobalStyles />
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 border-2 border-slate-600 border-t-cyan-400 rounded-full animate-spin"></div>
          <span className="text-slate-300">Loading tasks...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 text-white min-h-screen font-sans flex flex-col items-center p-4 sm:p-8">
      <GlobalStyles />
      <div className="w-full max-w-2xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl sm:text-5xl font-bold text-slate-100 tracking-tight">
            Zygonic
          </h1>
          <p className="text-slate-400 mt-2">Let's get the ball rolling, in your hands.</p>
        </header>

        {error && (
          <div className="mb-6 p-4 bg-red-900/50 border border-red-700 rounded-lg text-red-200">
            {error}
          </div>
        )}

        <main className="space-y-8">
          <div className="p-6 bg-slate-800/50 rounded-xl border border-slate-700 shadow-2xl">
            <AddTodoForm onAddTodo={addTask} />
          </div>

          <div className="flex justify-between items-center px-2 text-sm text-slate-400 font-medium">
            <span>Overall Progress: {overallProgress}%</span>
            <span>{completedCount} / {totalCount} Completed</span>
          </div>
          
          <div className="p-1">
            <TodoList 
              tasks={tasks} 
              onDeleteTask={deleteTask} 
              onUpdateProgress={updateTaskProgress}
              onUpdateText={updateTaskDescription}
            />
          </div>
        </main>

        <footer className="text-center mt-12 text-slate-600 text-sm">
          <p>Double-click a task to edit. Drag the slider to update progress.</p>
        </footer>
      </div>
    </div>
  );
};

export default App;