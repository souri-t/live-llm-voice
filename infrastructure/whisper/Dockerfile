FROM debian:bookworm-slim AS builder
ARG WHISPER_CPP_VERSION=v1.8.6
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates cmake g++ git make && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 --branch ${WHISPER_CPP_VERSION} https://github.com/ggml-org/whisper.cpp.git /src
WORKDIR /src
RUN cmake -B build -DWHISPER_BUILD_EXAMPLES=ON -DWHISPER_BUILD_SERVER=ON -DGGML_METAL=OFF \
    -DGGML_NATIVE=OFF -DGGML_CPU_ARM_ARCH="armv8.2-a+fp16" \
    && cmake --build build --config Release -j2 --target whisper-server

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl libgomp1 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /src/build/bin/whisper-server /usr/local/bin/whisper-server
COPY --from=builder /src/build/src/libwhisper.so* /usr/local/lib/
COPY --from=builder /src/build/ggml/src/libggml*.so* /usr/local/lib/
COPY download-model.sh /usr/local/bin/download-model
RUN chmod +x /usr/local/bin/download-model && ldconfig
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/download-model"]
