// Foundry Web UI — API Configuration

export const API_BASE = window.location.protocol === 'file:'
    ? 'http://localhost:8000'
    : window.location.origin;
