export interface Task {
  id: number;
  description: string;
  action: object;
  status: string;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface TaskRequest {
  description: string;
  status: string;
  progress: number;
}

export interface ApiResponse<T> {
  status_code: number;
  content: T;
}