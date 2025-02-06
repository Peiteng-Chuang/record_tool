import ctypes
import win32api
import screeninfo

PROCESS_PER_MONITOR_DPI_AWARE = 2
MDT_EFFECTIVE_DPI = 0

def get_dpi_from_monitor(index):
    shcore = ctypes.windll.shcore
    monitors = win32api.EnumDisplayMonitors()

    dpiX = ctypes.c_uint()
    dpiY = ctypes.c_uint()

    for i, monitor in enumerate(monitors):
        shcore.GetDpiForMonitor(
            monitor[0].handle,
            MDT_EFFECTIVE_DPI,
            ctypes.byref(dpiX),
            ctypes.byref(dpiY)
        )
        if i == index:
            return (dpiX.value, dpiY.value)
        
    return (96, 96)

#================================================================
def get_screen_info():
    screens = []
    monitors = screeninfo.get_monitors()

    user32 = ctypes.windll.user32
    shcore = ctypes.windll.shcore
    user32.SetProcessDPIAware()
    shcore.SetProcessDpiAwareness(2)  # 讓應用程式變成 Per Monitor DPI Aware
    
    for i, monitor in enumerate(monitors):
        print(f"***Processing Monitor {i + 1}: {monitor.name}***")
        
        # 使用 EnumDisplayMonitors 獲取每個顯示器的 HMONITOR
        hmonitor = win32api.MonitorFromPoint((monitor.x, monitor.y))
        monitor_info = win32api.GetMonitorInfo(hmonitor)

        print(f"  Monitor Info: {monitor_info}")
        
        work_area = monitor_info.get("Work")
        device_name = monitor_info.get("Device")
        
        dpi_x, dpi_y = get_dpi_from_monitor(i)
        
        scaling_factor_x = dpi_x / 96.0  # Windows default DPI is 96
        scaling_factor_y = dpi_y / 96.0  # Windows default DPI is 96
        
        screen_info = {
            "index": i,
            "name": f"Monitor {i + 1} ({device_name})" if device_name else f"Monitor {i + 1}",
            "width": monitor.width,
            "height": monitor.height,
            "dpi": (dpi_x, dpi_y),
            "scaling_factor_x": scaling_factor_x,
            "scaling_factor_y": scaling_factor_y,
            "x": monitor.x,
            "y": monitor.y,
            "work_area": work_area if work_area else (monitor.x, monitor.y, monitor.x + monitor.width, monitor.y + monitor.height),
            "top_left": (monitor.x, monitor.y),
            "top_right": (monitor.x + monitor.width, monitor.y),
            "bottom_left": (monitor.x, monitor.y + monitor.height),
            "bottom_right": (monitor.x + monitor.width, monitor.y + monitor.height),
        }
        screens.append(screen_info)
    
    return screens

def print_screen_info():
    screens = get_screen_info()
    print(f"Total Connected Screens: {len(screens)}\n")
    for screen in screens:
        print(f"{screen['name']}")
        print(f"  Resolution: {screen['width']}x{screen['height']}")
        print(f"  Work Area: {screen['work_area']}")
        print(f"  DPI: {screen['dpi']}")
        print(f"  Scaling Factor_x: {screen['scaling_factor_x']:.2f}")
        print(f"  Scaling Factor_y: {screen['scaling_factor_y']:.2f}")
        print(f"  Position: ({screen['x']}, {screen['y']})")
        print(f"  Corners:")
        print(f"    Top Left: {screen['top_left']}")
        print(f"    Top Right: {screen['top_right']}")
        print(f"    Bottom Left: {screen['bottom_left']}")
        print(f"    Bottom Right: {screen['bottom_right']}")
        print("")

if __name__ == "__main__":
    print_screen_info()
