const translations = {
  es: {
    eyebrow: "Serie histórica, montos reales y destinos académicos",
    title: "Becas mexicanas al extranjero, con trazabilidad y diseño público",
    lede:
      "Proyecto estático bilingüe para explorar la evolución histórica de las becas al extranjero publicadas por Conacyt, Conahcyt y Secihti.",
    kpi_count: "Becas registradas",
    kpi_amount: "Monto real acumulado (base 2020)",
    kpi_years: "Años cubiertos",
    yearly_title: "Serie anual",
    yearly_subtitle: "Resumen del número de becas y montos reales por año.",
    knowledge_area_title: "Áreas del conocimiento",
    knowledge_area_subtitle: "Evolución anual del número de becas por área.",
    degree_title: "Nivel de estudios",
    degree_subtitle: "Evolución anual del número de becas por nivel.",
    map_title: "Mapa anual de destinos",
    map_subtitle: "Círculos escalados por número de becas en el país destino del año seleccionado.",
    selected_year_count: "Becas del año",
    selected_year_amount: "Monto real del año",
    selected_year_top: "Destinos del año seleccionado",
    selected_year_institutions: "Instituciones del año seleccionado",
    selected_year_institutions_subtitle: "Tamaño del bloque según monto y detalle al pasar el cursor.",
    countries_title: "Destinos principales",
    countries_subtitle: "Países con mayor presencia en la serie integrada.",
    institutions_title: "Instituciones destino",
    institutions_subtitle: "Universidades y centros con más becas registradas.",
    coverage_unspecified: "Cobertura no indicada",
    partial_badge: "parcial",
    method_title: "Método",
    method_body:
      "El sitio consume datos procesados fuera de línea a partir de snapshots locales del padrón oficial. No estima pagos no publicados y prioriza trazabilidad, deduplicación conservadora y montos reales base 2020.",
    method_sources_title: "Fuentes",
    method_source_current: "SECIHTI. Padrón de beneficiarios vigente.",
    method_source_historical: "SECIHTI. Archivo histórico de becas y posgrados.",
    method_source_inflation:
      "INEGI. Índice Nacional de Precios al Consumidor (base para la deflactación alineada a 2020).",
    partial_note: "El año {year} es parcial: la fuente publicada cubre {coverage}.",
    treemap_nominal_note: "Para este año, el treemap usa monto nominal porque no hay deflactor disponible.",
    treemap_empty: "No hay datos suficientes para visualizar instituciones en este año.",
    tooltip_beneficiaries: "Personas beneficiarias",
    tooltip_real_amount: "Monto real base 2020",
    tooltip_nominal_amount: "Monto nominal",
    line_chart_empty: "No hay datos suficientes para esta visualización.",
    line_chart_series: "Serie",
    line_chart_count: "Becas",
    amount_unavailable: "No disponible",
    map_unavailable: "Mapa no disponible en esta copia local."
  },
  en: {
    eyebrow: "Historical series, real values, and academic destinations",
    title: "Mexican foreign scholarships, with traceability and public-facing design",
    lede:
      "Bilingual static project to explore the historical evolution of foreign scholarships published by Conacyt, Conahcyt, and Secihti.",
    kpi_count: "Recorded scholarships",
    kpi_amount: "Accumulated real amount (2020 base)",
    kpi_years: "Years covered",
    yearly_title: "Yearly series",
    yearly_subtitle: "Summary of scholarship counts and real amounts by year.",
    knowledge_area_title: "Knowledge areas",
    knowledge_area_subtitle: "Yearly evolution of scholarship counts by area.",
    degree_title: "Study level",
    degree_subtitle: "Yearly evolution of scholarship counts by degree level.",
    map_title: "Annual destination map",
    map_subtitle: "Circles scaled by scholarship count in the destination country for the selected year.",
    selected_year_count: "Scholarships in year",
    selected_year_amount: "Real amount in year",
    selected_year_top: "Destinations for selected year",
    selected_year_institutions: "Institutions for selected year",
    selected_year_institutions_subtitle: "Block size follows amount and hover shows the detail.",
    countries_title: "Top destinations",
    countries_subtitle: "Countries with the strongest presence in the integrated series.",
    institutions_title: "Destination institutions",
    institutions_subtitle: "Universities and centers with the highest scholarship counts.",
    coverage_unspecified: "Coverage not specified",
    partial_badge: "partial",
    method_title: "Method",
    method_body:
      "The site consumes offline processed data from local snapshots of the official registry. It does not estimate unpublished payments and prioritizes traceability, conservative deduplication, and 2020-based real values.",
    method_sources_title: "Sources",
    method_source_current: "SECIHTI. Current beneficiary registry.",
    method_source_historical: "SECIHTI. Historical scholarships and graduate archive.",
    method_source_inflation:
      "INEGI. National Consumer Price Index (used for the 2020-based deflation series).",
    partial_note: "Year {year} is partial: the published source covers {coverage}.",
    treemap_nominal_note: "For this year, the treemap uses nominal amounts because no deflator is available.",
    treemap_empty: "There is not enough data to visualize institutions for this year.",
    tooltip_beneficiaries: "Beneficiaries",
    tooltip_real_amount: "Real amount, 2020 base",
    tooltip_nominal_amount: "Nominal amount",
    line_chart_empty: "There is not enough data for this visualization.",
    line_chart_series: "Series",
    line_chart_count: "Scholarships",
    amount_unavailable: "Not available",
    map_unavailable: "Map not available in this local copy."
  }
};

const state = {
  currentLang: "es",
  summary: null,
  availableYears: [],
  selectedYear: null,
  mapContext: null
};

const COUNTRY_TRANSLATIONS = {
  "Alemania": "Germany",
  "Argentina": "Argentina",
  "Australia": "Australia",
  "Austria": "Austria",
  "Bélgica": "Belgium",
  "Bolivia": "Bolivia",
  "Bosnia y Herzegovina": "Bosnia and Herzegovina",
  "Brasil": "Brazil",
  "Canadá": "Canada",
  "Chile": "Chile",
  "China": "China",
  "Colombia": "Colombia",
  "Corea del Sur": "South Korea",
  "Costa Rica": "Costa Rica",
  "Croacia": "Croatia",
  "Cuba": "Cuba",
  "Dinamarca": "Denmark",
  "Ecuador": "Ecuador",
  "Egipto": "Egypt",
  "El Salvador": "El Salvador",
  "Eslovaquia": "Slovakia",
  "España": "Spain",
  "Estados Unidos": "United States",
  "Estonia": "Estonia",
  "Finlandia": "Finland",
  "Francia": "France",
  "Grecia": "Greece",
  "Guatemala": "Guatemala",
  "Hong Kong": "Hong Kong",
  "Hungría": "Hungary",
  "India": "India",
  "Indonesia": "Indonesia",
  "Irlanda": "Ireland",
  "Islandia": "Iceland",
  "Israel": "Israel",
  "Italia": "Italy",
  "Japón": "Japan",
  "Letonia": "Latvia",
  "Lituania": "Lithuania",
  "Luxemburgo": "Luxembourg",
  "Malasia": "Malaysia",
  "Noruega": "Norway",
  "Nueva Zelanda": "New Zealand",
  "Países Bajos": "Netherlands",
  "Panamá": "Panama",
  "Perú": "Peru",
  "Polonia": "Poland",
  "Portugal": "Portugal",
  "Puerto Rico": "Puerto Rico",
  "Reino Unido": "United Kingdom",
  "República Checa": "Czech Republic",
  "República Dominicana": "Dominican Republic",
  "Rusia": "Russia",
  "Singapur": "Singapore",
  "Sudáfrica": "South Africa",
  "Suecia": "Sweden",
  "Suiza": "Switzerland",
  "Tailandia": "Thailand",
  "Taiwán": "Taiwan",
  "Turquía": "Turkey",
  "Ucrania": "Ukraine",
  "Uruguay": "Uruguay",
  "Vietnam": "Vietnam"
};

const KNOWLEDGE_AREA_TRANSLATIONS = {
  "-": "Unspecified",
  "Agropecuarias y ecosistemas": "Agriculture and ecosystems",
  "Biología y química": "Biology and chemistry",
  "Biotecnología y agropecuarias": "Biotechnology and agriculture",
  "Ciencias sociales": "Social sciences",
  "Conducta y educación": "Behavior and education",
  "Físico-matemáticas y ciencias de la Tierra": "Physical sciences, mathematics, and Earth sciences",
  "Humanidades": "Humanities",
  "Humanidades y conducta": "Humanities and behavior",
  "IX. INTERDISCIPLINARIA": "IX. Interdisciplinary",
  "Ingenierías": "Engineering",
  "Medicina y salud": "Medicine and health",
  "VIII. INGENIERIAS Y DESARROLLO TECNOLOGICO": "VIII. Engineering and technological development"
};

const DEGREE_TRANSLATIONS = {
  "Doctorado": "Doctorate",
  "Especialidad": "Specialization",
  "Estancia técnica": "Technical stay",
  "Licenciatura": "Bachelor's",
  "Maestría": "Master's",
  "S/D": "Unknown",
  "Sabática": "Sabbatical"
};

const COVERAGE_TRANSLATIONS = {
  "Enero-Diciembre": "January-December",
  "Enero-Marzo": "January-March",
  "Cobertura no indicada": "Coverage not specified"
};

const INSTITUTION_TRANSLATIONS = {
  "UNIVERSIDAD DE BARCELONA": "University of Barcelona",
  "UNIVERSIDAD AUTONOMA DE BARCELONA": "Autonomous University of Barcelona",
  "UNIVERSITAT AUTONOMA DE BARCELONA": "Autonomous University of Barcelona",
  "UNIVERSIDAD COMPLUTENSE DE MADRID": "Complutense University of Madrid",
  "UNIVERSIDAD DE LA HABANA": "University of Havana",
  "UNIVERSIDAD POLITECNICA DE CATALUNA": "Polytechnic University of Catalonia",
  "UNIVERSITAT POLITECNICA DE CATALUNYA": "Polytechnic University of Catalonia",
  "UNIVERSIDAD POLITECNICA DE MADRID": "Technical University of Madrid",
  "UNIVERSIDAD POLITECNICA DE VALENCIA": "Polytechnic University of Valencia",
  "UNIVERSIDAD DE SALAMANCA": "University of Salamanca",
  "UNIVERSIDAD POMPEU FABRA": "Pompeu Fabra University",
  "UNIVERSIDAD AUTONOMA DE MADRID": "Autonomous University of Madrid",
  "MINISTERIO DE SALUD PUBLICA CUBA": "Ministry of Public Health of Cuba",
  "COMERCIALIZADORA DE SERVICIOS MEDICOS CUBANOS": "Cuban Medical Services Trading Company",
  "COMERCIALIZADORA DE SERVICIOS MEDICOS CUBANOS, S.A.": "Cuban Medical Services Trading Company, Inc."
};

function t(key, replacements = {}) {
  const template = translations[state.currentLang][key] || key;
  return Object.entries(replacements).reduce(
    (value, [token, replacement]) => value.replace(`{${token}}`, replacement),
    template
  );
}

function formatNumber(value) {
  const locale = state.currentLang === "es" ? "es-MX-u-nu-latn" : "en-US";
  return new Intl.NumberFormat(locale).format(value || 0);
}

function formatMoney(value) {
  const locale = state.currentLang === "es" ? "es-MX-u-nu-latn" : "en-US";
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency: "MXN",
    maximumFractionDigits: 0
  }).format(value || 0);
}

function formatMaybeMoney(value) {
  if (value === "" || value === null || value === undefined || Number.isNaN(Number(value))) {
    return t("amount_unavailable");
  }
  return formatMoney(Number(value));
}

function translateCountryName(value) {
  if (state.currentLang !== "en") {
    return value || "-";
  }
  return COUNTRY_TRANSLATIONS[value] || value || "-";
}

function translateCoverageLabel(value) {
  if (state.currentLang !== "en") {
    return value || t("coverage_unspecified");
  }
  return COVERAGE_TRANSLATIONS[value] || value || t("coverage_unspecified");
}

function translateKnowledgeAreaLabel(value) {
  if (state.currentLang !== "en") {
    return value || "-";
  }
  return KNOWLEDGE_AREA_TRANSLATIONS[value] || value || "-";
}

function translateDegreeLabel(value) {
  if (state.currentLang !== "en") {
    return value || "-";
  }
  return DEGREE_TRANSLATIONS[value] || value || "-";
}

function translateInstitutionName(value) {
  if (state.currentLang !== "en") {
    return value || "-";
  }
  return INSTITUTION_TRANSLATIONS[value] || value || "-";
}

function translateLabelByKey(labelKey, value) {
  if (labelKey === "country_canonical") {
    return translateCountryName(value);
  }
  if (labelKey === "institution_canonical") {
    return translateInstitutionName(value);
  }
  if (labelKey === "knowledge_area_label") {
    return translateKnowledgeAreaLabel(value);
  }
  if (labelKey === "degree_label") {
    return translateDegreeLabel(value);
  }
  return value || "-";
}

function applyTranslations() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.getAttribute("data-i18n");
    node.textContent = t(key);
  });
  document.documentElement.lang = state.currentLang;
}

function getYearlyLookup() {
  return new Map((state.summary.yearly || []).map((row) => [Number(row.source_year), row]));
}

function getYearMeta(year) {
  const matches = (state.summary.year_metadata || []).find((row) => Number(row.source_year) === Number(year));
  return matches || { coverage_label: "", is_partial_period: false };
}

function getSelectedYearRows() {
  return (state.summary.country_yearly || [])
    .filter((row) => Number(row.source_year) === Number(state.selectedYear))
    .sort((left, right) => Number(right.scholarship_count || 0) - Number(left.scholarship_count || 0));
}

function getSelectedYearInstitutionRows() {
  return (state.summary.institution_yearly || [])
    .filter((row) => Number(row.source_year) === Number(state.selectedYear))
    .sort((left, right) => Number(right.scholarship_count || 0) - Number(left.scholarship_count || 0));
}

function getTreemapAmount(row) {
  return Number(row.amount_visual_mxn || 0);
}

function getTreemapAmountLabel(row) {
  const basisKey = row.amount_visual_basis === "nominal" ? "tooltip_nominal_amount" : "tooltip_real_amount";
  return `${t(basisKey)}: ${formatMaybeMoney(row.amount_visual_mxn)}`;
}

function updateYearSelection(nextYear) {
  state.selectedYear = Number(nextYear);
  renderBars();
  renderYearPanel();
}

function shiftYear(step) {
  const index = state.availableYears.indexOf(state.selectedYear);
  const nextIndex = Math.max(0, Math.min(state.availableYears.length - 1, index + step));
  updateYearSelection(state.availableYears[nextIndex]);
}

function renderBars() {
  const container = document.getElementById("yearly-chart");
  container.innerHTML = "";
  const yearly = state.summary.yearly || [];
  const values = yearly.map((row) => Number(row.scholarship_count || 0));
  const max = Math.max(...values, 1);

  yearly.forEach((row) => {
    const year = Number(row.source_year);
    const count = Number(row.scholarship_count || 0);
    const width = `${(count / max) * 100}%`;
    const isActive = year === state.selectedYear;
    const badge = row.is_partial_period ? `<span class="year-subtle">${t("partial_badge")}</span>` : "";
    const item = document.createElement("button");
    item.type = "button";
    item.className = `bar-row ${isActive ? "is-active" : ""}`;
    item.innerHTML = `
      <span class="year-label"><span class="year-main">${row.source_year || "-"}</span>${badge}</span>
      <div class="bar-track"><div class="bar-fill" style="width: ${width};"></div></div>
      <span class="bar-value metric">${formatNumber(count)}</span>
    `;
    item.addEventListener("click", () => {
      updateYearSelection(year);
      syncYearControls();
    });
    container.appendChild(item);
  });
}

function renderRanking(elementId, rows, labelKey) {
  const list = document.getElementById(elementId);
  list.innerHTML = "";
  rows.forEach((row) => {
    const item = document.createElement("li");
    item.innerHTML = `
      <strong>${translateLabelByKey(labelKey, row[labelKey])}</strong><br />
      <span class="metric">${formatNumber(Number(row.scholarship_count || 0))} | ${formatMaybeMoney(
        row.amount_real_mxn_2020
      )}</span>
    `;
    list.appendChild(item);
  });
}

function getTopSeries(rows, labelKey, limit = 6) {
  const totals = new Map();
  rows.forEach((row) => {
    const label = row[labelKey];
    const count = Number(row.scholarship_count || 0);
    totals.set(label, (totals.get(label) || 0) + count);
  });
  return [...totals.entries()]
    .sort((left, right) => right[1] - left[1])
    .slice(0, limit)
    .map(([label]) => label);
}

function renderLineChart(containerId, legendId, rows, labelKey) {
  const container = document.getElementById(containerId);
  const legend = document.getElementById(legendId);
  container.innerHTML = "";
  legend.innerHTML = "";

  if (!rows.length) {
    container.innerHTML = `<div class="line-chart-empty">${t("line_chart_empty")}</div>`;
    return;
  }

  const years = [...new Set(rows.map((row) => Number(row.source_year)))].sort((left, right) => left - right);
  const topSeries = getTopSeries(rows, labelKey, 6);
  const palette = ["#0b6e4f", "#1f4e79", "#8a5a13", "#5f0f40", "#285943", "#7c3a2d"];

  const series = topSeries.map((label, index) => {
    const values = years.map((year) => {
      const match = rows.find((row) => Number(row.source_year) === year && row[labelKey] === label);
      return { year, count: Number(match?.scholarship_count || 0) };
    });
    return { label, translatedLabel: translateLabelByKey(labelKey, label), color: palette[index % palette.length], values };
  });

  const maxCount = Math.max(...series.flatMap((serie) => serie.values.map((value) => value.count)), 1);
  const width = container.clientWidth || 520;
  const height = 280;
  const margin = { top: 16, right: 16, bottom: 30, left: 42 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const yearStep = years.length > 1 ? plotWidth / (years.length - 1) : 0;

  const svgParts = [
    `<svg class="line-chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet">`,
    `<line x1="${margin.left}" y1="${margin.top + plotHeight}" x2="${margin.left + plotWidth}" y2="${margin.top + plotHeight}" class="axis-line" />`,
    `<line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${margin.top + plotHeight}" class="axis-line" />`
  ];

  const tickCount = 4;
  for (let tick = 0; tick <= tickCount; tick += 1) {
    const value = (maxCount / tickCount) * tick;
    const y = margin.top + plotHeight - (value / maxCount) * plotHeight;
    svgParts.push(`<line x1="${margin.left}" y1="${y}" x2="${margin.left + plotWidth}" y2="${y}" class="grid-line" />`);
    svgParts.push(
      `<text x="${margin.left - 8}" y="${y + 4}" text-anchor="end" class="axis-label">${formatNumber(Math.round(value))}</text>`
    );
  }

  years.forEach((year, index) => {
    const x = margin.left + yearStep * index;
    svgParts.push(
      `<text x="${x}" y="${height - 8}" text-anchor="middle" class="axis-label">${year}</text>`
    );
  });

  series.forEach((serie) => {
    const points = serie.values
      .map((value, index) => {
        const x = margin.left + yearStep * index;
        const y = margin.top + plotHeight - (value.count / maxCount) * plotHeight;
        return `${x},${y}`;
      })
      .join(" ");
    svgParts.push(`<polyline points="${points}" fill="none" stroke="${serie.color}" stroke-width="3" />`);
    serie.values.forEach((value, index) => {
      const x = margin.left + yearStep * index;
      const y = margin.top + plotHeight - (value.count / maxCount) * plotHeight;
      svgParts.push(
        `<circle cx="${x}" cy="${y}" r="4" fill="${serie.color}"><title>${t("line_chart_series")}: ${serie.translatedLabel}\n${value.year}\n${t("line_chart_count")}: ${formatNumber(value.count)}</title></circle>`
      );
    });
  });

  svgParts.push("</svg>");
  container.innerHTML = svgParts.join("");

  series.forEach((serie) => {
    const item = document.createElement("div");
    item.className = "legend-item";
    item.innerHTML = `
      <span class="legend-swatch" style="background:${serie.color};"></span>
      <span>${serie.translatedLabel}</span>
    `;
    legend.appendChild(item);
  });
}

function buildTreemapLayout(rows, x, y, width, height) {
  if (!rows.length) {
    return [];
  }
  if (rows.length === 1) {
    return [{ ...rows[0], x, y, width, height }];
  }

  const total = rows.reduce((sum, row) => sum + getTreemapAmount(row), 0);
  if (total <= 0) {
    return rows.map((row, index) => ({
      ...row,
      x,
      y: y + (height / rows.length) * index,
      width,
      height: height / rows.length
    }));
  }

  let running = 0;
  let splitIndex = 0;
  for (let index = 0; index < rows.length; index += 1) {
    running += getTreemapAmount(rows[index]);
    splitIndex = index + 1;
    if (running >= total / 2) {
      break;
    }
  }

  const leftGroup = rows.slice(0, splitIndex);
  const rightGroup = rows.slice(splitIndex);
  if (!rightGroup.length) {
    return rows.map((row, index) => ({
      ...row,
      x: x + (width / rows.length) * index,
      y,
      width: width / rows.length,
      height
    }));
  }

  const leftTotal = leftGroup.reduce((sum, row) => sum + getTreemapAmount(row), 0);
  if (width >= height) {
    const leftWidth = width * (leftTotal / total);
    return [
      ...buildTreemapLayout(leftGroup, x, y, leftWidth, height),
      ...buildTreemapLayout(rightGroup, x + leftWidth, y, width - leftWidth, height)
    ];
  }

  const topHeight = height * (leftTotal / total);
  return [
    ...buildTreemapLayout(leftGroup, x, y, width, topHeight),
    ...buildTreemapLayout(rightGroup, x, y + topHeight, width, height - topHeight)
  ];
}

function renderInstitutionTreemap(rows) {
  const container = document.getElementById("selected-year-institution-treemap");
  const note = document.getElementById("selected-year-institution-note");
  container.innerHTML = "";

  const filteredRows = rows
    .filter((row) => row.institution_canonical && getTreemapAmount(row) > 0)
    .slice(0, 28);

  if (!filteredRows.length) {
    note.hidden = true;
    container.innerHTML = `<div class="treemap-empty">${t("treemap_empty")}</div>`;
    return;
  }

  const hasNominalFallback = filteredRows.some((row) => row.amount_visual_basis === "nominal");
  note.hidden = !hasNominalFallback;
  note.textContent = hasNominalFallback ? t("treemap_nominal_note") : "";

  const width = container.clientWidth || 320;
  const height = Math.max(container.clientHeight || 420, 420);
  const layout = buildTreemapLayout(filteredRows, 0, 0, width, height);

  const tooltip = document.createElement("div");
  tooltip.className = "treemap-tooltip";
  tooltip.hidden = true;
  container.appendChild(tooltip);

  layout.forEach((row) => {
    const tile = document.createElement("div");
    tile.className = "treemap-tile";
    const palette = [
      "#0b6e4f",
      "#1f4e79",
      "#5f0f40",
      "#8a5a13",
      "#285943",
      "#7c3a2d"
    ];
    tile.style.backgroundColor = palette[layout.indexOf(row) % palette.length];
    tile.style.left = `${row.x}px`;
    tile.style.top = `${row.y}px`;
    tile.style.width = `${Math.max(row.width - 4, 0)}px`;
    tile.style.height = `${Math.max(row.height - 4, 0)}px`;

    const area = row.width * row.height;
    const showName = area >= 2200;
    const showAmount = area >= 4200;
    if (showName) {
      tile.innerHTML = `
        <strong>${translateInstitutionName(row.institution_canonical)}</strong>
        ${showAmount ? `<span>${formatMaybeMoney(row.amount_visual_mxn)}</span>` : ""}
      `;
    }

    tile.addEventListener("mousemove", (event) => {
      tooltip.hidden = false;
      tooltip.innerHTML = `
        <strong>${translateInstitutionName(row.institution_canonical)}</strong>
        <span>${getTreemapAmountLabel(row)}</span>
        <span>${t("tooltip_beneficiaries")}: ${formatNumber(Number(row.scholarship_count || 0))}</span>
      `;
      const rect = container.getBoundingClientRect ? container.getBoundingClientRect() : { left: 0, top: 0 };
      const offsetX = (event.clientX || 0) - rect.left;
      const offsetY = (event.clientY || 0) - rect.top;
      tooltip.style.left = `${Math.max(8, Math.min(offsetX + 18, width - 188))}px`;
      tooltip.style.top = `${Math.max(8, Math.min(offsetY + 18, height - 98))}px`;
    });
    tile.addEventListener("mouseleave", () => {
      tooltip.hidden = true;
    });
    container.appendChild(tile);
  });
}

function ensureMap() {
  if (state.mapContext) {
    return state.mapContext;
  }

  const root = document.getElementById("world-map-root");
  if (!root || !window.__WORLD_MAP_SVG__) {
    if (root) {
      root.textContent = t("map_unavailable");
    }
    return null;
  }

  root.innerHTML = `<div class="map-base"></div>`;
  const base = root.querySelector(".map-base");
  base.innerHTML = window.__WORLD_MAP_SVG__;
  const baseSvg = base.querySelector("svg");
  if (!baseSvg) {
    root.textContent = t("map_unavailable");
    return null;
  }

  baseSvg.classList.add("world-map-svg");
  baseSvg.setAttribute("preserveAspectRatio", "xMidYMid meet");

  const viewBox = (baseSvg.getAttribute("viewBox") || "0 0 800 460")
    .split(/\s+/)
    .map((value) => Number(value));

  const bubbleSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  bubbleSvg.setAttribute("viewBox", viewBox.join(" "));
  bubbleSvg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  bubbleSvg.classList.add("bubble-layer");
  root.appendChild(bubbleSvg);

  state.mapContext = { root, baseSvg, bubbleSvg };
  return state.mapContext;
}

function clearMapState(mapContext) {
  mapContext.bubbleSvg.innerHTML = "";
  mapContext.baseSvg.querySelectorAll(".is-active-country").forEach((node) => {
    node.classList.remove("is-active-country");
  });
}

function getMapAnchor(mapContext, mapCode) {
  const target = mapContext.baseSvg.querySelector(`[id="${mapCode}"]`);
  if (!target) {
    return null;
  }
  const mainland = typeof target.querySelector === "function" ? target.querySelector(".mainland") : null;
  const anchorTarget = mainland || target;
  const bbox = anchorTarget.getBBox();
  return {
    x: bbox.x + bbox.width / 2,
    y: bbox.y + bbox.height / 2,
    target: mainland || target
  };
}

function renderMap(rows) {
  const mapContext = ensureMap();
  if (!mapContext) {
    return;
  }

  clearMapState(mapContext);
  const validRows = rows.filter((row) => row.map_code);
  const maxCount = Math.max(...validRows.map((row) => Number(row.scholarship_count || 0)), 1);

  validRows.forEach((row) => {
    const anchor = getMapAnchor(mapContext, row.map_code);
    if (!anchor) {
      return;
    }

    anchor.target.classList.add("is-active-country");

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    const radius = 4 + Math.sqrt(Number(row.scholarship_count || 0) / maxCount) * 24;
    circle.setAttribute("cx", anchor.x);
    circle.setAttribute("cy", anchor.y);
    circle.setAttribute("r", radius.toFixed(2));
    circle.setAttribute("class", "map-bubble");

    const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
    title.textContent = `${translateCountryName(row.country_canonical)}: ${formatNumber(Number(row.scholarship_count || 0))}`;
    circle.appendChild(title);
    mapContext.bubbleSvg.appendChild(circle);
  });
}

function syncYearControls() {
  const slider = document.getElementById("year-slider");
  const index = Math.max(0, state.availableYears.indexOf(state.selectedYear));
  slider.max = String(Math.max(0, state.availableYears.length - 1));
  slider.value = String(index);
  document.getElementById("year-prev").disabled = index === 0;
  document.getElementById("year-next").disabled = index === state.availableYears.length - 1;
}

function renderYearPanel() {
  const year = state.selectedYear;
  const yearlyLookup = getYearlyLookup();
  const yearlyRow = yearlyLookup.get(year) || {};
  const yearMeta = getYearMeta(year);
  const selectedRows = getSelectedYearRows();
  const selectedInstitutionRows = getSelectedYearInstitutionRows();

  document.getElementById("selected-year-label").textContent = String(year || "-");
  document.getElementById("selected-year-coverage").textContent =
    translateCoverageLabel(yearMeta.coverage_label);
  document.getElementById("selected-year-count").textContent = formatNumber(
    Number(yearlyRow.scholarship_count || 0)
  );
  document.getElementById("selected-year-amount").textContent = formatMaybeMoney(
    yearlyRow.amount_real_mxn_2020
  );

  const partialNote = document.getElementById("partial-note");
  if (yearMeta.is_partial_period) {
    partialNote.hidden = false;
    partialNote.textContent = t("partial_note", {
      year: String(year),
      coverage: translateCoverageLabel(yearMeta.coverage_label)
    });
  } else {
    partialNote.hidden = true;
    partialNote.textContent = "";
  }

  renderRanking("selected-year-country-list", selectedRows.slice(0, 10), "country_canonical");
  renderInstitutionTreemap(selectedInstitutionRows);
  renderMap(selectedRows);
  syncYearControls();
}

function renderSummary() {
  document.getElementById("kpi-count").textContent = formatNumber(
    Number(state.summary.kpis.scholarship_count || 0)
  );
  document.getElementById("kpi-amount").textContent = formatMoney(
    Number(state.summary.kpis.amount_real_mxn_2020 || 0)
  );
  document.getElementById("kpi-years").textContent = formatNumber(
    Number(state.summary.kpis.years_covered || 0)
  );

  renderBars();
  renderLineChart("knowledge-area-line-chart", "knowledge-area-legend", state.summary.knowledge_area_yearly || [], "knowledge_area_label");
  renderLineChart("degree-line-chart", "degree-legend", state.summary.degree_yearly || [], "degree_label");
  renderYearPanel();
  renderRanking("country-list", state.summary.top_countries || [], "country_canonical");
  renderRanking("institution-list", state.summary.top_institutions || [], "institution_canonical");
}

function bindControls() {
  document.getElementById("lang-toggle").addEventListener("click", () => {
    state.currentLang = state.currentLang === "es" ? "en" : "es";
    applyTranslations();
    renderSummary();
  });

  document.getElementById("year-slider").addEventListener("input", (event) => {
    const index = Number(event.target.value || 0);
    updateYearSelection(state.availableYears[index]);
  });

  document.getElementById("year-prev").addEventListener("click", () => {
    shiftYear(-1);
  });

  document.getElementById("year-next").addEventListener("click", () => {
    shiftYear(1);
  });
}

function bootstrap() {
  applyTranslations();
  state.summary = window.__SITE_SUMMARY__ || {
    kpis: { scholarship_count: 0, amount_real_mxn_2020: 0, years_covered: 0 },
    yearly: [],
    year_metadata: [],
    country_yearly: [],
    institution_yearly: [],
    knowledge_area_yearly: [],
    degree_yearly: [],
    top_countries: [],
    top_institutions: []
  };
  state.availableYears = (state.summary.available_years || []).map(Number).sort((left, right) => left - right);
  state.selectedYear = state.availableYears[state.availableYears.length - 1] || null;
  bindControls();
  renderSummary();
}

bootstrap();
