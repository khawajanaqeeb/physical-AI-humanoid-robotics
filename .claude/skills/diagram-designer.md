# Diagram Designer Skill

## Purpose
Create detailed descriptions and specifications for technical diagrams, illustrations, and visual aids for the textbook.

## Diagram Types
- **Mechanical Diagrams**: Robot structure, joint mechanisms, actuator assemblies
- **Block Diagrams**: Control systems, signal flow, system architecture
- **Circuit Diagrams**: Electronics, sensors, motor drivers, power systems
- **Flowcharts**: Algorithms, decision trees, process flows
- **Network Diagrams**: ROS node graphs, communication architectures
- **Conceptual Diagrams**: Abstract concepts, AI architectures, learning pipelines
- **Timeline Diagrams**: Historical development, research evolution
- **Comparison Charts**: Algorithm comparison, performance metrics

## When to Use This Skill
- Illustrating complex robotics mechanisms
- Visualizing control system architectures
- Creating step-by-step process diagrams
- Showing data flow in AI systems
- Depicting sensor configurations
- Explaining kinematic chains

## Output Format
Provide detailed diagram specifications including:

1. **Diagram Title**: Clear, descriptive title
2. **Purpose**: What the diagram illustrates and why
3. **Elements**: Detailed list of all components to include
4. **Layout**: Spatial arrangement and organization
5. **Labels**: All text labels, annotations, equations
6. **Connections**: Arrows, lines, relationships between elements
7. **Color Coding**: Suggested colors for different element types
8. **Dimensions**: Relative sizes and proportions
9. **Caption**: Educational caption explaining the diagram
10. **Tool Suggestion**: Recommended tool (Mermaid, PlantUML, Draw.io, etc.)

## Style Guidelines
- Keep diagrams clean and uncluttered
- Use consistent visual language throughout the textbook
- Ensure accessibility (colorblind-friendly palettes)
- Include legends for symbols and notation
- Make diagrams scalable and print-friendly
- Provide both simplified and detailed versions when helpful

## Example Description Format
```
DIAGRAM: Humanoid Robot Control Loop
TYPE: Block Diagram
ELEMENTS:
  - Sensor Block (blue): IMU, cameras, force sensors
  - Perception Module (green): State estimation, vision processing
  - Controller (orange): Whole-body controller, trajectory planner
  - Actuators (red): Motor commands, joint control
CONNECTIONS:
  - Sensor → Perception (sensor data)
  - Perception → Controller (robot state)
  - Controller → Actuators (control commands)
  - Actuators → Sensors (feedback loop)
CAPTION: Closed-loop control architecture for humanoid robot...
```
