import { Task, TaskRequest, ApiResponse } from './types';

const API_BASE_URL = 'http://localhost:8000';

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  async getAllTasks(): Promise<Task[]> {
    const response = await this.request<Task[]>('/all');
    return response.content;
  }

  async createTask(description: string, status: string = 'NEW', progress: number = 0): Promise<number> {
    const taskRequest: TaskRequest = {
      description,
      status,
      progress,
    };
    
    const response = await this.request<number>('/new', {
      method: 'POST',
      body: JSON.stringify(taskRequest),
    });
    
    return response.content;
  }

  async updateTask(id: number, updates: Partial<TaskRequest>): Promise<void> {
    await this.request(`/update?task_id=${id}`, {
      method: 'POST',
      body: JSON.stringify(updates),
    });
  }

  async deleteTask(id: number): Promise<void> {
    await this.request(`/delete?task_id=${id}`, {
      method: 'DELETE',
    });
  }

  async startTask(id: number): Promise<void> {
    await this.request(`/start?task_id=${id}`, {
      method: 'POST',
    });
  }
}

export const apiService = new ApiService();