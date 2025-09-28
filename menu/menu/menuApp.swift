//
//  menuApp.swift
//  menu
//
//  Created by Jerry Zhu on 9/27/25.

import SwiftUI

@main
struct MenuApp: App {
    @State private var tasks: [Task] = [] // Start with empty array
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
                            TaskRowView(task: $tasks[index])
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
    
    private func addNewTask() {
        guard !newTaskName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            return
        }
        
        let colors: [Color] = [.blue, .green, .orange, .red, .pink, .mint, .purple, .cyan]
        let randomColor = colors.randomElement() ?? .blue
        
        let newTask = Task(
            title: newTaskName.trimmingCharacters(in: .whitespacesAndNewlines),
            status: "",
            color: randomColor,
            isCompleted: false,
            progress: 0.0
        )
        tasks.append(newTask)
        newTaskName = "" // Clear the text field
    }
}

struct Task {
    var title: String
    var status: String
    var color: Color
    var isCompleted: Bool
    var progress: Double // 0.0 to 100.0
}

struct TaskRowView: View {
    @Binding var task: Task
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
                    .padding(.horizontal, 12)
                    .padding(.vertical, 10)
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
                        }
                )
            }
            .frame(height: 44)
        }
        .padding(.vertical, 1)
        .scaleEffect(isAnimating ? 1.05 : 1.0)
        .opacity(task.isCompleted ? (isAnimating ? 0.5 : 0.7) : 1.0)
        .animation(.easeInOut(duration: 0.15), value: isAnimating)
    }
}

#Preview {
    VStack {
        TaskRowView(task: .constant(Task(title: "email john", status: "not started", color: .pink, isCompleted: true, progress: 100.0)))
        TaskRowView(task: .constant(Task(title: "project 1", status: "", color: .orange, isCompleted: false, progress: 75.0)))
    }
    .frame(width: 320)
    .padding()
}
