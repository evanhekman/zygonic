//
//  menuApp.swift
//  menu
//
//  Created by Jerry Zhu on 9/27/25.

import SwiftUI

@main
struct MenuApp: App {
    @State private var tasks: [Task] = {
        // Initialize with loaded tasks
        return loadInitialTasks()
    }()
    @State private var newTaskName: String = ""
    
    var body: some Scene {
        MenuBarExtra {
            VStack(spacing: 0) {
                // Header
                Text("Zygonic")
                    .font(.title2)
                    .fontWeight(.bold)
                    .padding(.bottom, 8)
                
                // Scrollable task list
                ScrollView {
                    LazyVStack(spacing: 0) {
                        ForEach(tasks.indices, id: \.self) { index in
                            TaskRowView(
                                task: $tasks[index],
                                onTaskUpdate: { updatedTask in
                                    updateTask(updatedTask, at: index)
                                },
                                onDelete: {
                                    deleteTask(at: index)
                                }
                            )
                        }
                    }
                }
                .frame(height: 300) // Fixed height - always 300 points
                
                // Add new task input (fixed at bottom)
                VStack(spacing: 8) {
                    TextField("Enter task name", text: $newTaskName)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .onSubmit {
                            addNewTask()
                        }
                    
                    Button(action: {
                        addNewTask()
                    }) {
                        HStack {
                            Spacer()
                            Text("Add New Task")
                                .font(.headline)
                                .foregroundColor(.primary)
                            Spacer()
                        }
                        .padding()
                        .background(Color.gray.opacity(0.1))
                    }
                    .buttonStyle(PlainButtonStyle())
                    .cornerRadius(8)
                }
                .padding(.top, 8)
            }
            .frame(width: 320)
            .padding(.horizontal, 8)
            .padding(.vertical, 8)
        } label: {
            Image("MenuIcon")
        }
        .menuBarExtraStyle(.window)
    }
    
    // MARK: - Database-Ready Functions
    
    /// Load initial tasks when app starts (static function for initialization)
    private static func loadInitialTasks() -> [Task] {
        // TODO: Replace with actual database call
        // e.g., return DatabaseManager.shared.fetchAllTasks()
        return []
    }
    
    /// Reload tasks from storage (for refreshing during runtime)
    private func reloadTasks() {
        // TODO: Replace with actual database call
        // e.g., tasks = DatabaseManager.shared.fetchAllTasks()
        tasks = Self.loadInitialTasks()
    }
    
    /// Add a new task to storage
    private func addNewTask() {
        guard !newTaskName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            return
        }
        
        let trimmedName = newTaskName.trimmingCharacters(in: .whitespacesAndNewlines)
        let newTask = createTask(title: trimmedName)
        
        // Add to local array
        insertTask(newTask)
        
        // Clear input
        newTaskName = ""
    }
    
    /// Create a new task with default values
    private func createTask(title: String) -> Task {
        let colors: [Color] = [.blue, .green, .orange, .red, .pink, .mint, .purple, .cyan]
        let randomColor = colors.randomElement() ?? .blue
        
        return Task(
            id: UUID(), // Add unique ID for database operations
            title: title,
            status: "",
            color: randomColor,
            isCompleted: false,
            progress: 0.0
        )
    }
    
    /// Insert a task into storage
    private func insertTask(_ task: Task) {
        // TODO: Replace with database insert
        // e.g., DatabaseManager.shared.insertTask(task)
        tasks.append(task)
    }
    
    /// Update an existing task in storage
    private func updateTask(_ task: Task, at index: Int) {
        guard index < tasks.count else { return }
        
        // TODO: Replace with database update
        // e.g., DatabaseManager.shared.updateTask(task)
        tasks[index] = task
    }
    
    /// Delete a task from storage
    private func deleteTask(at index: Int) {
        guard index < tasks.count else { return }
        
        let task = tasks[index]
        
        // TODO: Replace with database delete
        // e.g., DatabaseManager.shared.deleteTask(task.id)
        tasks.remove(at: index)
    }
    
    /// Delete a task by ID
    private func deleteTask(withId id: UUID) {
        guard let index = tasks.firstIndex(where: { $0.id == id }) else { return }
        deleteTask(at: index)
    }
}

struct Task {
    let id: UUID // Added for database operations
    var title: String
    var status: String
    var color: Color
    var isCompleted: Bool
    var progress: Double // 0.0 to 100.0
}

struct TaskRowView: View {
    @Binding var task: Task
    let onTaskUpdate: (Task) -> Void
    let onDelete: () -> Void
    @State private var isAnimating = false
    
    var body: some View {
        HStack(spacing: 8) {
            // Checkbox
            Button(action: {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.6, blendDuration: 0)) {
                    task.isCompleted.toggle()
                    if task.isCompleted {
                        task.progress = 100.0
                        // Trigger completion animation
                        isAnimating = true
                        
                        // Reset animation state after delay
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                            isAnimating = false
                        }
                    }
                    // Notify parent of the update
                    onTaskUpdate(task)
                }
            }) {
                Image(systemName: task.isCompleted ? "checkmark.square" : "square")
                    .foregroundColor(task.isCompleted ? .green : .gray)
                    .font(.system(size: 16, weight: .medium))
            }
            .buttonStyle(PlainButtonStyle())
            .frame(width: 24, height: 24)
            
            // Task slider bar with custom drag gesture
            GeometryReader { geometry in
                ZStack {
                    // Background progress bar
                    HStack(spacing: 0) {
                        // Filled portion
                        Rectangle()
                            .fill(task.color)
                            .frame(width: geometry.size.width * (task.progress / 100.0))
                        
                        // Unfilled portion
                        Rectangle()
                            .fill(task.color.opacity(0.2))
                    }
                    .cornerRadius(6)
                    
                    // Task title overlay
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            if task.status.isEmpty {
                                Text(task.title)
                                    .font(.system(size: 14, weight: .medium))
                                    .foregroundColor(task.progress < 50 ? .primary : .white)
                            } else {
                                Text("\(task.title) (\(task.status))")
                                    .font(.system(size: 14, weight: .medium))
                                    .foregroundColor(.white)
                            }
                        }
                        Spacer()
                        
                        // Progress percentage
                        Text("\(Int(task.progress))%")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(task.progress < 50 ? .primary : .white)
                            .opacity(0.8)
                    }
                    .padding(.leading, 12)
                    .padding(.trailing, 30)
                }
                .gesture(
                    DragGesture(minimumDistance: 0)
                        .onChanged { value in
                            let newProgress = (value.location.x / geometry.size.width) * 100.0
                            task.progress = max(0, min(100, newProgress))
                            
                            if task.progress >= 100 {
                                task.isCompleted = true
                            } else {
                                task.isCompleted = false
                            }
                            // Notify parent of the update
                            onTaskUpdate(task)
                        }
                )
            }
            .frame(height: 44)
        }
        .overlay(alignment: .trailing) {
            Button(role: .destructive, action: onDelete) {
                Image(systemName: "trash")
                    .font(.system(size: 13, weight: .semibold))
                    .padding(6)                    // decent hit target
            }
            .buttonStyle(PlainButtonStyle())
            .help("Delete task")
            .keyboardShortcut(.delete, modifiers: []) // optional: ⌫ when row is focused
            .padding(.trailing, 2)
        }
        .padding(.vertical, 1)
        .scaleEffect(isAnimating ? 1.05 : 1.0)
        .opacity(task.isCompleted ? (isAnimating ? 0.5 : 0.7) : 1.0)
        .animation(.easeInOut(duration: 0.15), value: isAnimating)
    }
}
