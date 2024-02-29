import subprocess

def get_column_in_command():
  command = "docker ps -a --size"
  col = -4
  try:
    result = subprocess.run(command.split(), capture_output=True, text=True, check=True)
    output = result.stdout
  except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
    return None

  # Split the output lines
  lines = output.splitlines()

  # Skip the header row (optional, depending on the command)
  # lines = lines[1:]

  # Extract the second column using list comprehension
  ans = [line.split()[col] for line in lines if line.strip()][1:]

  return ans


res = get_column_in_command()

if res:
  print(res)
else:
  print("Failed to retrieve data.")
