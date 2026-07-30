import subprocess
import time
import sys

def run_tunnel():
    print("🚀 Starting localtunnel on port 5000...")
    print("📋 Copy the 'url' provided below and paste it into your bot.py game_url variable!\n")
    
    try:
        # Using npx localtunnel to expose port 5000
        process = subprocess.Popen(
            ["npx", "localtunnel", "--port", "5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                sys.stdout.write(output)
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        print("\n🛑 Tunnel stopped by user.")
    except Exception as e:
        print(f"\n❌ Error starting tunnel: {e}")
        print("💡 Make sure Node.js is installed so 'npx' is available on your system.")

if __name__ == "__main__":
    run_tunnel()