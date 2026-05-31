FROM osrf/ros:jazzy-desktop

RUN apt-get update && apt-get install -y \
    ros-jazzy-plotjuggler-ros \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY . /ws/dynamicalnodes/
RUN python3 -m venv /opt/venv --system-site-packages && \
    /opt/venv/bin/pip install /ws/dynamicalnodes jupyterlab

ENV PATH="/opt/venv/bin:$PATH"

RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc

WORKDIR /ws/dynamicalnodes

EXPOSE 8888

CMD ["bash"]
