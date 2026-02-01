IMAGE_NAME := image-tools
DOCKER_RUN := docker run --rm -v "$(HOME):$(HOME)" -w "$(PWD)" $(IMAGE_NAME)

.PHONY: build clean enhance remove-bg vectorize convert

build:
	docker build -t $(IMAGE_NAME) .

clean:
	docker rmi $(IMAGE_NAME)

# Usage: make enhance INPUT=screenshot.png [OUTPUT=output.png] [ARGS="-g sunset"]
enhance:
	$(DOCKER_RUN) /app/enhance_screenshot.py $(INPUT) $(OUTPUT) $(ARGS)

# Usage: make remove-bg INPUT=photo.jpg [OUTPUT=output.png] [ARGS="--color 255,255,255"]
remove-bg:
	$(DOCKER_RUN) /app/remove_bg.py $(INPUT) $(if $(OUTPUT),-o $(OUTPUT)) $(ARGS)

# Usage: make vectorize INPUT=logo.png [OUTPUT=logo.svg] [ARGS="--binary"]
vectorize:
	$(DOCKER_RUN) /app/vectorize_image.py $(INPUT) $(if $(OUTPUT),-o $(OUTPUT)) $(ARGS)

# Usage: make convert INPUT=image.png [OUTPUT=image.webp] [ARGS="-q 90"]
convert:
	$(DOCKER_RUN) /app/convert_image.py $(INPUT) $(OUTPUT) $(ARGS)
