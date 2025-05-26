import os

os.makedirs("machine_learning/models/saved", exist_ok=True)

with open("machine_learning/__init__.py", "w") as f:
    f.write("# Machine learning package\n")

with open("machine_learning/models/__init__.py", "w") as f:
    f.write("# Models package\n")

with open("machine_learning/models/saved/__init__.py", "w") as f:
    f.write("# Empty file to make this directory a package\n")

print("Directory structure created successfully!")