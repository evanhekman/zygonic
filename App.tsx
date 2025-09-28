import React, { useState, useEffect } from 'react';
// import { GoogleGenAI, Type } from "@google/genai";
import { Todo } from './types';
import { AddTodoForm } from './components/AddTodoForm';
import { TodoList } from './components/TodoList';

const App: React.FC = () => {
  const [todos, setTodos] = useState<Todo[]>(() => {
    try {
      const savedTodos = localStorage.getItem('todos');
      return savedTodos ? JSON.parse(savedTodos) : [];
    } catch (error) {
      console.error("Could not parse todos from localStorage", error);
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem('todos', JSON.stringify(todos));
  }, [todos]);

  const addTodo = async (text: string) => {
    // const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

    const newTodo: Todo = {
      id: crypto.randomUUID(),
      text,
      progress: 0,
      createdAt: Date.now(),
      isLoadingNextSteps: true,
      nextSteps: [],
    };
    setTodos(prevTodos => [...prevTodos, newTodo]);

    // try {
    //     const response = await ai.models.generateContent({
    //     model: 'gemini-2.5-flash',
    //     contents: `Given the task: "${text}", provide a few brief, actionable next steps to get started. Return a JSON object with a single key 'steps' which is an array of strings.`,
    //     config: {
    //       responseMimeType: "application/json",
    //       responseSchema: {
    //         type: Type.OBJECT,
    //         properties: {
    //           steps: {
    //             type: Type.ARRAY,
    //             items: {
    //               type: Type.STRING,
    //               description: 'An actionable next step.'
    //             },
    //           },
    //         },
    //       },
    //     }
    //   });
      
    //   const jsonResponse = JSON.parse(response.text);
    //   const steps = jsonResponse.steps || [];

    //   setTodos(prevTodos =>
    //     prevTodos.map(todo =>
    //       todo.id === newTodo.id
    //         ? { ...todo, nextSteps: steps, isLoadingNextSteps: false }
    //         : todo
    //     )
    //   );
    // } catch (error) {
    //   console.error("Error fetching next steps from Gemini API:", error);
    //   setTodos(prevTodos =>
    //     prevTodos.map(todo =>
    //       todo.id === newTodo.id
    //         ? { ...todo, isLoadingNextSteps: false, nextSteps: ['Could not generate suggestions.'] }
    //         : todo
    //     )
    //   );
    // }
  };

  const deleteTodo = (id: string) => {
    setTodos(prevTodos => prevTodos.filter(todo => todo.id !== id));
  };
  
  const updateTodoText = (id: string, text: string) => {
    setTodos(prevTodos => 
      prevTodos.map(todo => 
        todo.id === id ? { ...todo, text } : todo
      )
    );
  };

  const updateTodoProgress = (id: string, progress: number) => {
    setTodos(prevTodos => 
      prevTodos.map(todo => 
        todo.id === id ? { ...todo, progress } : todo
      )
    );
  };
  
  const completedCount = todos.filter(t => t.progress === 100).length;
  const totalCount = todos.length;
  const overallProgress = totalCount > 0 ? Math.round(todos.reduce((sum, todo) => sum + todo.progress, 0) / totalCount) : 0;


  return (
    <div className="bg-slate-900 text-white min-h-screen font-sans flex flex-col items-center p-4 sm:p-8">
      <div className="w-full max-w-2xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl sm:text-5xl font-bold text-slate-100 tracking-tight">
            Zygonic
          </h1>
          <p className="text-slate-400 mt-2">Let's get the ball rolling, in your hands.</p>
        </header>

        <main className="space-y-8">
          <div className="p-6 bg-slate-800/50 rounded-xl border border-slate-700 shadow-2xl">
              <AddTodoForm onAddTodo={addTodo} />
          </div>

          <div className="flex justify-between items-center px-2 text-sm text-slate-400 font-medium">
            <span>Overall Progress: {overallProgress}%</span>
            <span>{completedCount} / {totalCount} Completed</span>
          </div>
          
          <div className="p-1">
            <TodoList 
              todos={todos} 
              onDeleteTodo={deleteTodo} 
              onUpdateProgress={updateTodoProgress}
              onUpdateText={updateTodoText}
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