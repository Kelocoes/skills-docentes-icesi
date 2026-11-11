// =================================================================
// CATEGORÍA 5 — SLIDES DE CONTENIDO
// =================================================================

import { _section, state } from '../utils/core.js';

/**
 * Slide estándar: Logo + título azul en header + área de contenido libre
 * Equivale a: \slideStandard{title}{content}
 * @param {string} title - Título del slide
 * @param {string} content - Contenido HTML (listas, párrafos, imágenes, Mermaid, etc.)
 */
export function slideStandard(title, content) {
  return _section('standard', `
  ${state.logoPosFn()}
  <div class="slide-header"><h2>${title}</h2></div>
  <div class="slide-content">${content}</div>
  `, 'blue', 'right');
}

/**
 * Slide de dos columnas iguales
 * Equivale a: \slideTwoCols{title}{col1}{col2}
 * @param {string} title - Título del slide
 * @param {string} col1 - Contenido HTML de la columna izquierda
 * @param {string} col2 - Contenido HTML de la columna derecha
 */
export function slideTwoCols(title, col1, col2) {
  return _section('two-cols', `
  ${state.logoPosFn()}
  <div class="slide-header"><h2>${title}</h2></div>
  <div class="cols-container">
    <div class="col">${col1}</div>
    <div class="col">${col2}</div>
  </div>
  `, 'blue', 'right');
}

/**
 * Slide de tres columnas iguales
 * Equivale a: \slideThreeCols{title}{col1}{col2}{col3}
 * @param {string} title - Título del slide
 * @param {string} col1 - Contenido HTML de la columna 1
 * @param {string} col2 - Contenido HTML de la columna 2
 * @param {string} col3 - Contenido HTML de la columna 3
 */
export function slideThreeCols(title, col1, col2, col3) {
  return _section('three-cols', `
  ${state.logoPosFn()}
  <div class="slide-header"><h2>${title}</h2></div>
  <div class="cols-container">
    <div class="col">${col1}</div>
    <div class="col">${col2}</div>
    <div class="col">${col3}</div>
  </div>
  `, 'blue', 'right');
}

/**
 * Slide de dos tarjetas coloreadas en grid (2 columnas)
 * @param {string} title - Título del slide
 * @param {string} c1title - Título/Categoría de la tarjeta 1
 * @param {string} c1 - Contenido de la tarjeta 1
 * @param {string} c2title - Título/Categoría de la tarjeta 2
 * @param {string} c2 - Contenido de la tarjeta 2
 */
export function slideTwoCards(title, c1title, c1, c2title, c2) {
  function _card(colorClass, header, body) {
    return `<div class="card ${colorClass}">
      <div class="card-header">${header}</div>
      <div class="card-body">${body}</div>
    </div>`;
  }
  return _section('four-cards cards-grid-2-slide', `
  ${state.logoPosFn()}
  <div class="slide-header"><h2>${title}</h2></div>
  <div class="cards-grid cards-grid-2">
    ${_card('blue',   c1title, c1)}
    ${_card('green',  c2title, c2)}
  </div>
  `, 'blue', 'right');
}

/**
 * Slide de tres tarjetas coloreadas en grid (3 columnas)
 * @param {string} title - Título del slide
 * @param {string} c1title - Título de la tarjeta 1
 * @param {string} c1 - Contenido de la tarjeta 1
 * @param {string} c2title - Título de la tarjeta 2
 * @param {string} c2 - Contenido de la tarjeta 2
 * @param {string} c3title - Título de la tarjeta 3
 * @param {string} c3 - Contenido de la tarjeta 3
 */
export function slideThreeCards(title, c1title, c1, c2title, c2, c3title, c3) {
  function _card(colorClass, header, body) {
    return `<div class="card ${colorClass}">
      <div class="card-header">${header}</div>
      <div class="card-body">${body}</div>
    </div>`;
  }
  return _section('four-cards cards-grid-3-slide', `
  ${state.logoPosFn()}
  <div class="slide-header"><h2>${title}</h2></div>
  <div class="cards-grid cards-grid-3">
    ${_card('blue',   c1title, c1)}
    ${_card('purple', c2title, c2)}
    ${_card('orange', c3title, c3)}
  </div>
  `, 'blue', 'right');
}

/**
 * Slide de cuatro tarjetas coloreadas en grid
 * Equivale a: \slideFourCards{title}{c1title}{c1content}...
 * @param {string} title - Título del slide
 * @param {string} c1title - Título de la tarjeta 1 (azul)
 * @param {string} c1 - Contenido de la tarjeta 1
 * @param {string} c2title - Título de la tarjeta 2 (morado)
 * @param {string} c2 - Contenido de la tarjeta 2
 * @param {string} c3title - Título de la tarjeta 3 (naranja)
 * @param {string} c3 - Contenido de la tarjeta 3
 * @param {string} c4title - Título de la tarjeta 4 (verde)
 * @param {string} c4 - Contenido de la tarjeta 4
 */
export function slideFourCards(title, c1title, c1, c2title, c2, c3title, c3, c4title, c4) {
  function _card(colorClass, header, body) {
    return `<div class="card ${colorClass}">
      <div class="card-header">${header}</div>
      <div class="card-body">${body}</div>
    </div>`;
  }
  return _section('four-cards', `
  ${state.logoPosFn()}
  <div class="slide-header"><h2>${title}</h2></div>
  <div class="cards-bg"></div>
  <div class="cards-grid">
    ${_card('blue',   c1title, c1)}
    ${_card('purple', c2title, c2)}
    ${_card('orange', c3title, c3)}
    ${_card('green',  c4title, c4)}
  </div>
  `, 'blue', 'right');
}

/**
 * Slide de tarjetas flexibles dinámicas (acepta un array de N tarjetas)
 * @param {string} title - Título del slide
 * @param {Array<{title: string, body: string, color?: string, icon?: string}>} cards - Lista de tarjetas
 */
export function slideCards(title, cards = []) {
  const colors = ['blue', 'purple', 'orange', 'green', 'blue', 'purple'];
  const gridClass = cards.length === 2 ? 'cards-grid-2' : cards.length === 3 ? 'cards-grid-3' : cards.length > 4 ? 'cards-grid-6' : '';
  
  const cardsHtml = cards.map((c, i) => {
    const colorClass = c.color || colors[i % colors.length];
    const iconHtml = c.icon ? `<span class="card-icon-slot" style="margin-right:8px; display:inline-flex; align-items:center; vertical-align:middle;">${c.icon}</span>` : '';
    return `<div class="card ${colorClass}">
      <div class="card-header" style="display:flex; align-items:center; gap:8px;">${iconHtml}<span>${c.title}</span></div>
      <div class="card-body">${c.body}</div>
    </div>`;
  }).join('');

  return _section('four-cards dynamic-cards-slide', `
  ${state.logoPosFn()}
  <div class="slide-header"><h2>${title}</h2></div>
  <div class="cards-grid ${gridClass}">
    ${cardsHtml}
  </div>
  `, 'blue', 'right');
}

