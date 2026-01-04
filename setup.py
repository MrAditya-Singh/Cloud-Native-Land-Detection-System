from setuptools import setup, find_packages

setup(
    name="cloud-native-land-detection",
    version="0.1.0",
    description="AWS-based ML system for land detection using satellite data",
    author="Cloud Native Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "boto3>=1.28.0",
        "sentinelsat>=1.2.1",
        "landsatxplore>=0.14.0",
        "numpy>=1.24.0",
        "rasterio>=1.3.0",
        "geopandas>=0.14.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "schedule>=1.2.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "moto>=4.2.0",
        ],
    },
    python_requires=">=3.8",
)
