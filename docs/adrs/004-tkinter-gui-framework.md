# ADR-004: Tkinter GUI Framework

## Status

Accepted

## Context

The application needed a graphical user interface that would:
- Be cross-platform compatible
- Have minimal external dependencies
- Provide a native look and feel
- Support both simple and complex user interactions
- Be easy to maintain and extend
- Work well with the existing Python codebase
- Support both GUI and command-line operation modes

The target users are individuals managing personal finances who need an intuitive interface for file selection, progress feedback, and basic configuration. The solution needed to balance simplicity with functionality while maintaining the ability to run without GUI dependencies.

## Decision

We chose Tkinter as the GUI framework with the following architecture:

1. **Tkinter as Primary GUI Framework**: Using Python's built-in Tkinter library
2. **Graceful Degradation**: Fallback to command-line interface when GUI unavailable
3. **Modular GUI Design**: Separate GUI components for different functionalities
4. **Consistent Styling**: Custom styling for professional appearance
5. **Error Handling**: Comprehensive error handling for GUI operations

### Key Implementation Details

#### GUI Architecture
- **MainGUI** (`main_gui.py`): Main application window and navigation controller
- **ImporterGUI** (`importer_gui.py`): Import operation interface
- **AutoCategorizeGUI** (`auto_categorize_gui.py`): Auto-categorization interface
- **Frame-Based Navigation**: Multiple frames within a single window

#### Styling and Theming
- **Custom Styles**: Professional styling using ttk styles
- **Consistent Colors**: Teal-based color scheme (#008080)
- **Modern Layout**: Card-based design with proper spacing
- **Responsive Design**: Window centering and proper sizing

#### Error Handling
- **Import Error Handling**: Graceful handling of missing Tkinter
- **User Feedback**: Clear progress indicators and status messages
- **Validation**: Input validation with user-friendly error messages

## Consequences

### Positive Consequences
- **No External Dependencies**: Tkinter is included with Python
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Native Look**: Uses system-native widgets and styling
- **Lightweight**: Minimal memory and resource usage
- **Python Integration**: Seamless integration with existing Python code
- **Graceful Degradation**: Can fall back to command-line when GUI unavailable
- **Rapid Development**: Quick to implement and modify

### Negative Consequences
- **Limited Modern Features**: Lacks some modern GUI features
- **Styling Limitations**: Limited control over appearance compared to modern frameworks
- **Complex Layouts**: More complex layouts require more code
- **Platform Differences**: Subtle differences in appearance across platforms
- **Performance**: May not handle very large datasets as efficiently as web-based interfaces

### Testing Implications
- **GUI Testing**: Requires GUI testing frameworks or headless testing
- **Platform Testing**: Need to test across different operating systems
- **Error Scenario Testing**: Test GUI error conditions and fallback behavior
- **User Interaction Testing**: Test file dialogs, button clicks, and form submissions
- **Styling Testing**: Verify consistent appearance across platforms

## Compliance

### Testing Standards Compliance
- **Unit Tests**: GUI components can be unit tested with proper mocking
- **Integration Tests**: End-to-end GUI workflow testing
- **Error Handling Tests**: Test GUI error conditions and fallback behavior
- **Platform Tests**: Cross-platform compatibility testing
- **Accessibility Tests**: Basic accessibility compliance testing

### Code Standards Compliance
See [Architecture Standards](../architecture-standards.md) for comprehensive code standards including:
- **PEP 8 Compliance**: Style guidelines and formatting
- **Type Hints**: Comprehensive type annotations for GUI components
- **Documentation**: Component and API documentation
- **Error Handling**: See [Architecture Standards](../architecture-standards.md) for error handling patterns

### Security Compliance
- **Input Validation**: All GUI inputs are validated before processing
- **File Dialog Security**: Secure file selection and validation
- **Error Messages**: Secure error messages that don't expose system details
- **Permission Handling**: Proper handling of file permission errors

## Implementation Example

```python
class CashSyncApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cash Sync")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        self.center_window()
        self.setup_styles()
        
        # Frame-based navigation
        self.frames = {}
        for F in (MainMenuFrame, ImporterGUIFrame, AutoCategorizeFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
```

## Error Handling Strategy

### GUI Unavailable
```python
try:
    app = CashSyncApp()
    app.run()
except (ImportError, ModuleNotFoundError, OSError) as e:
    logger.error("Error starting GUI: %s", e)
    logger.error("Please ensure tkinter is installed: pip install tkinter")
    sys.exit(1)
```

### Graceful Degradation
- Fallback to command-line interface when GUI unavailable
- Clear error messages with installation instructions
- Maintain full functionality through command-line

## Styling Guidelines

### Color Scheme
- **Primary**: #008080 (Teal)
- **Background**: #f0f0f0 (Light Gray)
- **Cards**: #ffffff (White)
- **Text**: #333333 (Dark Gray)
- **Secondary Text**: #666666 (Medium Gray)

### Typography
- **Title**: Arial, 24pt, Bold
- **Subtitle**: Arial, 12pt
- **Body**: Arial, 11pt
- **Small**: Arial, 10pt

## References

- [Architecture Documentation](../architecture.md)
- [Testing Standards](../testing-standards/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [ttk Documentation](https://docs.python.org/3/library/tkinter.ttk.html)
