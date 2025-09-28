export interface Todo {
  id: string;
  text: string;
  progress: number;
  createdAt: number;
  nextSteps?: string[];
  isLoadingNextSteps?: boolean;
}