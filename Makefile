include makefiles/*.mk

.DEFAULT_GOAL := help

help:
	@echo "Ambientes disponibles:"
	@echo "  local    - Desarrollo local"
	@echo "  dev      - Desarrollo remoto" 
	@echo "  staging  - Pre-producción"
	@echo "  prod     - Producción"


	