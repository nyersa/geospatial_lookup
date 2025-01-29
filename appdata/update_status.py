def update_status(message, status_var, root):
    status_var.set(message)
    root.update_idletasks()