FROM osrf/ros:jazzy-desktop

RUN apt-get update && apt-get install -y \
    ros-jazzy-plotjuggler-ros \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY . /ws/dynamicalnodes/
RUN pip install /ws/dynamicalnodes jupyterlab --break-system-packages

EXPOSE 8888

CMD ["bash"]
