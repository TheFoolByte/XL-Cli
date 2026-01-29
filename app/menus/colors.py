"""
Color utility module for CLI styling.
Theme: Cyan, Grey, White, Yellow
"""

# ANSI Color Codes
class Colors:
    # Reset
    RESET = '\033[0m'
    
    # White
    WHITE = '\033[38;5;255m'
    BRIGHT_WHITE = '\033[1;37m'
    
    # Grey variants
    LIGHT_GREY = '\033[38;5;250m'
    GREY = '\033[38;5;245m'
    DARK_GREY = '\033[38;5;240m'
    DIM_GREY = '\033[38;5;236m'
    
    # Cyan variants
    CYAN = '\033[38;5;51m'
    SOFT_CYAN = '\033[38;5;87m'
    DARK_CYAN = '\033[38;5;37m'
    
    # Yellow variants
    YELLOW = '\033[38;5;226m'
    SOFT_YELLOW = '\033[38;5;229m'
    GOLD = '\033[38;5;220m'
    
    # Text styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Status colors
    RED = '\033[38;5;196m'
    GREEN = '\033[38;5;46m'

# Quick color functions
def white(text):
    return f"{Colors.WHITE}{text}{Colors.RESET}"

def grey(text):
    return f"{Colors.GREY}{text}{Colors.RESET}"

def cyan(text):
    return f"{Colors.CYAN}{text}{Colors.RESET}"

def yellow(text):
    return f"{Colors.YELLOW}{text}{Colors.RESET}"

def bold(text):
    return f"{Colors.BOLD}{text}{Colors.RESET}"

def dim(text):
    return f"{Colors.DIM}{text}{Colors.RESET}"

# Styled elements
WIDTH = 55

def section_header(title, width=WIDTH):
    """Create styled section header: ─── TITLE ───"""
    title_with_spaces = f" {title} "
    padding = width - len(title_with_spaces) - 2
    left_pad = padding // 2
    right_pad = padding - left_pad
    return f"{Colors.DARK_GREY}{'─' * left_pad}{Colors.CYAN}{title_with_spaces}{Colors.DARK_GREY}{'─' * right_pad}{Colors.RESET}"

def box_line(width=WIDTH, char='─'):
    """Create a horizontal box line"""
    return f"{Colors.DIM_GREY}{char * width}{Colors.RESET}"

def box_top(width=WIDTH):
    """Create box top border"""
    return f"{Colors.DARK_GREY}┌{'─' * (width-2)}┐{Colors.RESET}"

def box_bottom(width=WIDTH):
    """Create box bottom border"""
    return f"{Colors.DARK_GREY}└{'─' * (width-2)}┘{Colors.RESET}"

def menu_item(num, text, highlight=False):
    """Create styled menu item"""
    if highlight:
        return f"  {Colors.YELLOW}{num}{Colors.DARK_GREY}.{Colors.RESET} {Colors.WHITE}{text}{Colors.RESET}"
    return f"  {Colors.CYAN}{num}{Colors.DARK_GREY}.{Colors.RESET} {Colors.LIGHT_GREY}{text}{Colors.RESET}"

def menu_item_special(num, text):
    """Create styled special menu item (for letters/back options)"""
    return f"  {Colors.SOFT_YELLOW}{num}{Colors.DARK_GREY}.{Colors.RESET} {Colors.GREY}{text}{Colors.RESET}"

def info_line(label, value, label_width=12):
    """Create info line like 'Nomor:    6285xxx'"""
    padded_label = f"{label}:".ljust(label_width)
    return f"  {Colors.GREY}{padded_label}{Colors.RESET}{Colors.WHITE}{value}{Colors.RESET}"

def success(text):
    """Success message"""
    return f"{Colors.CYAN}✓ {text}{Colors.RESET}"

def error(text):
    """Error message"""
    return f"{Colors.YELLOW}✗ {text}{Colors.RESET}"

def warning(text):
    """Warning message"""
    return f"{Colors.GOLD}! {text}{Colors.RESET}"

def prompt(text=""):
    """Input prompt styling"""
    return f"{Colors.GREY}{text}{Colors.RESET}"

def title(text):
    """Title text"""
    return f"{Colors.CYAN}{text}{Colors.RESET}"

def highlight(text):
    """Highlighted text"""
    return f"{Colors.YELLOW}{text}{Colors.RESET}"

def data(text):
    """Data value text"""
    return f"{Colors.WHITE}{text}{Colors.RESET}"

def label(text):
    """Label text"""
    return f"{Colors.GREY}{text}{Colors.RESET}"

# ASCII Art with theme colors
def get_colored_logo():
    """Return the ASCII art logo with theme colors"""
    logo = f"""
{Colors.DARK_GREY}            _____                    _____          
           /\\    \\                  /\\    \\         
          /::\\____\\                /::\\    \\        
         /::::|   |               /::::\\    \\       
        /:::::|   |              /::::::\\    \\      
       /::::::|   |             /:::/\\:::\\    \\     
      /:::/|::|   |            /:::/__\\:::\\    \\    
     /:::/ |::|   |           /::::\\   \\:::\\    \\   
    /:::/  |::|___|______    /::::::\\   \\:::\\    \\  
   {Colors.GREY}/:::/   |::::::::\\    \\  /:::/\\:::\\   \\:::\\    \\ 
  /:::/    |:::::::::\\____\\/:::/__\\:::\\   \\:::\\____\\
  \\::/    / ~~~~~/:::/    /\\:::\\   \\:::\\   \\::/    /
   \\/____/      /:::/    /  \\:::\\   \\:::\\   \\/____/ 
               /:::/    /    \\:::\\   \\:::\\    \\     
              {Colors.CYAN}/:::/    /      \\:::\\   \\:::\\____\\    
             /:::/    /        \\:::\\   \\::/    /    
            /:::/    /          \\:::\\   \\/____/     
           /:::/    /            \\:::\\    \\         
          {Colors.WHITE}/:::/    /              \\:::\\____\\        
          \\::/    /                \\::/    /        
           \\/____/                  \\/____/         {Colors.RESET}
"""
    return logo
