FROM nvcr.io/nvidia/cuda:11.6.1-cudnn8-devel-ubuntu20.04 as build

ENV DEBIAN_FRONTEND=noninteractive
ENV OPENCV_VERSION=4.8.0

ENV VIRTUAL_ENV=/opt/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends  \
        build-essential gcc g++ git wget cmake  unzip pkg-config  \
        python3 python3-dev                                   \
        python3-setuptools python3-pip python3-venv  \
        libavcodec-dev libavformat-dev libswscale-dev \
        libpng-dev libjpeg-dev libopenexr-dev libtiff-dev libwebp-dev \ 
        libopenblas-dev libatlas-base-dev liblapack-dev gfortran  \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /opt
RUN python3 -m venv $VIRTUAL_ENV && \ pip3 install wheel numpy

RUN wget https://github.com/opencv/opencv/archive/$OPENCV_VERSION.zip &&\
    unzip $OPENCV_VERSION.zip &&\
    rm $OPENCV_VERSION.zip &&\
    wget https://github.com/opencv/opencv_contrib/archive/$OPENCV_VERSION.zip &&\
    unzip ${OPENCV_VERSION}.zip &&\
    rm ${OPENCV_VERSION}.zip &&\
    mkdir /opt/opencv-${OPENCV_VERSION}/build && cd /opt/opencv-${OPENCV_VERSION}/build &&\
    cmake \
        -D OPENCV_EXTRA_MODULES_PATH=/opt/opencv_contrib-${OPENCV_VERSION}/modules \
        -D WITH_CUDA=ON \
        -D WITH_CUDNN=ON \ 
        -D OPENCV_DNN_CUDA=ON \
        -D ENABLE_FAST_MATH=ON \
        -D CUDA_FAST_MATH=ON \
        -D WITH_CUBLAS=ON \
        -D CUDA_ARCH_BIN=5.3,6.1,7.0,7.2,7.5,8.6 \
        -D BUILD_OPENCV_PYTHON3=ON \
        -D BUILD_OPENCV_PYTHON2=OFF \
        -D BUILD_OPENCV_JAVA=OFF \
        -D BUILD_TESTS=OFF \
        -D BUILD_IPP_IW=OFF \
        -D BUILD_PERF_TESTS=OFF \
        -D BUILD_EXAMPLES=OFF \
        -D BUILD_ANDROID_EXAMPLES=OFF \
        -D BUILD_DOCS=OFF \
        -D BUILD_ITT=OFF \
        -D INSTALL_PYTHON_EXAMPLES=OFF \
        -D INSTALL_C_EXAMPLES=OFF \
        -D INSTALL_TESTS=OFF \
        -D CMAKE_BUILD_TYPE=RELEASE \
        -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} \
        -D PYTHON_EXECUTABLE=${VIRTUAL_ENV}/bin/python3 \
        -D PYTHON_PACKAGES_PATH=${VIRTUAL_ENV}/lib/python3.8/site-packages \
        .. && \
    make -j4 && \
    make install && \
    ldconfig && \
    rm -rf /opt/opencv-${OPENCV_VERSION} && \
    rm -rf /opt/opencv_contrib-${OPENCV_VERSION}

WORKDIR /opt/is-face-detector
COPY . .

RUN pip3 install -r requirements.txt && \
    cd is_face_detector

FROM nvcr.io/nvidia/cuda:11.6.1-cudnn8-runtime-ubuntu20.04
COPY --from=build /opt/.venv /opt/.venv
COPY --from=build /opt/is-face-detector/model /opt/is-face-detector/model

ENV VIRTUAL_ENV=/opt/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && \
    apt-get install --no-install-recommends -y python3 \
    libavcodec-dev libavformat-dev libswscale-dev \
    libpng-dev libjpeg-dev libopenexr-dev libtiff-dev libwebp-dev && \
    rm -rf /var/lib/apt/lists/*

CMD ["python3", "/is_person_detector/stream.py"]
