# Tailscale Setup for Review GUI

This guide walks you through setting up Tailscale to securely access the AI Radio Review GUI remotely from any device.

## What is Tailscale?

Tailscale creates a secure VPN network between your devices, allowing you to access your Review GUI from anywhere without exposing it to the public internet.

## Installation

### Step 1: Install Tailscale

**Windows (this machine):**
```powershell
# Download and run the installer from:
# https://tailscale.com/download/windows

# Or use winget:
winget install tailscale.tailscale
```

**Other Devices (phone, tablet, laptop):**
- Download from: https://tailscale.com/download
- Available for macOS, Linux, iOS, Android, etc.

### Step 2: Sign In to Tailscale

1. After installation, launch Tailscale
2. Click "Sign In" and authenticate (supports Google, Microsoft, GitHub, etc.)
3. Tailscale will assign your machine a permanent IP address (e.g., `100.x.y.z`)

### Step 3: Get Your Tailscale IP

**Windows:**
```powershell
# Open PowerShell and run:
tailscale ip -4
```

This will show your Tailscale IPv4 address (something like `100.64.0.1`)

### Step 4: Configure Review GUI for Network Access

The Review GUI needs to accept connections from all network interfaces (not just localhost).

Update the launch script to bind to `0.0.0.0`:

```python
# In run_review_gui.py, change the streamlit run command:
subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    str(gui_script),
    "--server.port=8501",
    "--server.address=0.0.0.0",  # Add this line
    "--server.headless=true",
    "--browser.gatherUsageStats=false"
], cwd=str(project_root), check=True)
```

### Step 5: Configure Windows Firewall

Allow Streamlit through Windows Firewall:

```powershell
# Run as Administrator:
New-NetFirewallRule -DisplayName "Streamlit Review GUI" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 8501 `
  -Action Allow `
  -Profile Private
```

Or manually:
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Choose "Port" → TCP → 8501
5. Allow the connection → Apply to Private networks
6. Name it "Streamlit Review GUI"

## Usage

### Starting the Review GUI

On your Windows machine:

```powershell
# Activate venv and run
.\.venv\Scripts\python run_review_gui.py
```

### Accessing from Other Devices

1. Install Tailscale on the other device
2. Sign in with the same account
3. Get the Windows machine's Tailscale IP:
   ```powershell
   tailscale ip -4
   ```
4. Open a browser and navigate to:
   ```
   http://100.x.y.z:8501
   ```
   (Replace `100.x.y.z` with your actual Tailscale IP)

### Example URLs

- **From Windows machine:** `http://localhost:8501` or `http://100.x.y.z:8501`
- **From phone/tablet:** `http://100.x.y.z:8501`
- **From laptop:** `http://100.x.y.z:8501`

## Security Notes

✅ **Secure:**
- Tailscale uses WireGuard encryption
- Only devices on your Tailscale network can access the GUI
- No public internet exposure
- Tailscale handles authentication

✅ **Private:**
- Traffic is end-to-end encrypted
- Tailscale can't see your traffic
- No port forwarding needed on your router

## Troubleshooting

### Can't connect from other device

1. **Check Tailscale is running on both devices:**
   ```powershell
   tailscale status
   ```

2. **Verify firewall rule:**
   ```powershell
   Get-NetFirewallRule -DisplayName "Streamlit Review GUI"
   ```

3. **Test connectivity:**
   ```powershell
   # From the other device, ping the Windows machine
   ping 100.x.y.z
   ```

4. **Check Review GUI is running:**
   ```powershell
   netstat -ano | findstr :8501
   ```

### Streamlit not accessible

Make sure you added `--server.address=0.0.0.0` to the launch command, not just `--server.headless=true`.

### Connection refused

1. Verify the Review GUI is running
2. Check the firewall allows port 8501
3. Confirm you're using the correct Tailscale IP

## Advanced: MagicDNS

Tailscale includes MagicDNS for easier access:

1. Enable MagicDNS in Tailscale admin console: https://login.tailscale.com/admin/dns
2. Set a machine name (e.g., "windows-desktop")
3. Access via: `http://windows-desktop:8501`

## Quick Reference

| Task | Command |
|------|---------|
| Get Tailscale IP | `tailscale ip -4` |
| Check Tailscale status | `tailscale status` |
| View connected devices | `tailscale status` |
| Start Review GUI | `.\.venv\Scripts\python run_review_gui.py` |
| Check port 8501 | `netstat -ano \| findstr :8501` |

## Next Steps

After Tailscale is set up:

1. Test accessing the Review GUI from another device
2. Bookmark the URL on your mobile devices
3. Consider enabling [Tailscale SSH](https://tailscale.com/kb/1193/tailscale-ssh/) for full remote access
4. Review Tailscale's [ACL policies](https://tailscale.com/kb/1018/acls/) for finer-grained access control

## Resources

- [Tailscale Documentation](https://tailscale.com/kb/)
- [Streamlit Networking](https://docs.streamlit.io/library/advanced-features/configuration)
- [Review GUI Documentation](REVIEW_GUI.md)
