//
//  menuApp.swift
//  menu
//
//  Created by Jerry Zhu on 9/27/25.
//

import SwiftUI

@main
struct MenuApp: App {
    var body: some Scene {
        // Creates a menu bar item with a star icon
        MenuBarExtra {
            Button("Test") {
                print("Test clicked")
            }
        } label: {
            Image("MenuIcon")
        }
    }
}
