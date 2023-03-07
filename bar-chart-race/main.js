import './style.css'



////////////////////////////////////////////////////////////////
// Constants
const topN = 26; // show top N names
const k = 10; // interpolate data for k steps
var data;
var names;
var keyFramesGlobal;
var prev;
var next;
const duration = 150; // animation duration between keyframes in milliseconds
const margin = ({ top: 16, right: 6, bottom: 6, left: 0 });
const barSize = 48;
const height = margin.top + barSize * topN + margin.bottom;
const width = 1280;
const y = d3.scaleBand()
  .domain(d3.range(topN + 1))
  .rangeRound([margin.top, margin.top + barSize * (topN + 1 + 0.1)])
  .padding(0.1);
const x = d3.scaleLinear([0, 1], [margin.left, width - margin.right]);

////////////////////////////////////////////////////////////////
// Data Prep Helper functions

// open the csv file and read the data
const getData = async (file) => {
  return await d3.csv(file, d3.autoType);
}

// get all names
const getNames = (data) => {
  return new Set(data.map(d => d.name));
}

// get all categories
const getCategories = (data) => {
  return new Set(data.map(d => d.category));
}

// group the data by name
const groupData = (data) => {
  return d3.group(data, d => d.name);
}

// get dataValues: a nested map from date and name to value
const getDataValues = (data) => {
  return Array.from(d3.rollup(data, ([d]) => d.value, d => +d.date, d => d.name))
    .map(([date, data]) => [new Date(date), data])
    .sort(([a], [b]) => d3.ascending(a, b))
}

// The rank function below takes a value accessor function, 
// retrieves each item's value, 
// sorts the result by descending value, 
// and then assigns rank.
const rank = (value) => {
  const data = Array.from(names, name => ({ name, value: value(name) }));
  data.sort((a, b) => d3.descending(a.value, b.value));
  for (let i = 0; i < data.length; ++i) data[i].rank = Math.min(topN, i);
  return data;
}

// get keyFrames
const getKeyFrames = (dateValues) => {
  const keyframes = [];
  let ka, a, kb, b;
  for ([[ka, a], [kb, b]] of d3.pairs(dateValues)) {
    for (let i = 0; i < k; ++i) {
      const t = i / k;
      keyframes.push([
        new Date(ka * (1 - t) + kb * t),
        rank(name => (a.get(name) || 0) * (1 - t) + (b.get(name) || 0) * t)
      ]);
    }
  }
  keyframes.push([new Date(kb), rank(name => b.get(name) || 0)]);
  return keyframes;
}

// get nameFrames from keyFrames
const getNameFrames = (keyFrames) => {
  return d3.groups(keyFrames.flatMap(([, data]) => data), d => d.name);
}

// get prev and next from nameFrames
const getPrevNext = (nameFrames) => {
  const prev = new Map(nameFrames.flatMap(([, data]) => d3.pairs(data, (a, b) => [b, a])));
  const next = new Map(nameFrames.flatMap(([, data]) => d3.pairs(data)));
  return [prev, next];
}

////////////////////////////////////////////////////////////////
// Drawing Helper functions

const color = () => {
  const scale = d3.scaleOrdinal(d3.schemeTableau10);
  if (data.some(d => d.category !== undefined)) {
    const categoryByName = new Map(data.map(d => [d.name, d.category]));
    scale.domain(Array.from(categoryByName.values()));
    return d => scale(categoryByName.get(d.name));
  }
  return d => scale(d.name);
}

const drawBars = (svg) => {
  let bar = svg.append("g")
    .attr("fill-opacity", 0.6)
    .selectAll("rect");

  return ([date, data], transition) => bar = bar
    .data(data.slice(0, topN), d => d.name)
    .join(
      enter => enter.append("rect")
        .attr("fill", color())
        .attr("height", y.bandwidth())
        .attr("x", x(0))
        .attr("y", d => y((prev.get(d) || d).rank))
        .attr("width", d => x((prev.get(d) || d).value) - x(0)),
      update => update,
      exit => exit.transition(transition).remove()
        .attr("y", d => y((next.get(d) || d).rank))
        .attr("width", d => x((next.get(d) || d).value) - x(0))
    )
    .call(bar => bar.transition(transition)
      .attr("y", d => y(d.rank))
      .attr("width", d => x(d.value) - x(0)));
}

const textTween = (a, b) => {
  const i = d3.interpolateNumber(a, b);
  return function (t) {
    this.textContent = d3.format(",d")(i(t));
  };
}

const drawLabels = (svg) => {
  let label = svg.append("g")
    .style("font", "bold 12px var(--sans-serif)")
    .style("font-variant-numeric", "tabular-nums")
    .attr("text-anchor", "end")
    .selectAll("text");

  return ([date, data], transition) => label = label
    .data(data.slice(0, topN), d => d.name)
    .join(
      enter => enter.append("text")
        .attr("transform", d => `translate(${x((prev.get(d) || d).value)},${y((prev.get(d) || d).rank)})`)
        .attr("y", y.bandwidth() / 2)
        .attr("x", -6)
        .attr("dy", "-0.25em")
        .text(d => d.name)
        .call(text => text.append("tspan")
          .attr("fill-opacity", 0.7)
          .attr("font-weight", "normal")
          .attr("x", -6)
          .attr("dy", "1.15em")),
      update => update,
      exit => exit.transition(transition).remove()
        .attr("transform", d => `translate(${x((next.get(d) || d).value)},${y((next.get(d) || d).rank)})`)
        .call(g => g.select("tspan").tween("text", d => textTween(d.value, (next.get(d) || d).value)))
    )
    .call(bar => bar.transition(transition)
      .attr("transform", d => `translate(${x(d.value)},${y(d.rank)})`)
      .attr("id", "labelOnBar")
      .call(g => g.select("tspan").tween("text", d => textTween((prev.get(d) || d).value, d.value))));
}

const drawAxis = (svg) => {
  const g = svg.append("g")
    .attr("transform", `translate(0,${margin.top})`);

  const axis = d3.axisTop(x)
    .ticks(width / 160)
    .tickSizeOuter(0)
    .tickSizeInner(-barSize * (topN + y.padding()));

  return (_, transition) => {
    g.transition(transition).call(axis);
    g.select(".tick:first-of-type text").remove();
    g.selectAll(".tick:not(:first-of-type) line").attr("stroke", "#242424");
    g.select(".domain").remove();
  };
}

const formatDate = d3.utcFormat("%B %Y");

const drawTicker = (svg) => {
  const now = svg.append("text")
    // .style("font", `bold ${barSize}px var(--sans-serif)`)
    // .style("font-variant-numeric", "tabular-nums")
    .attr("text-anchor", "end")
    .attr("x", width - 6)
    .attr("y", margin.top + barSize * (topN - 0.45))
    .attr("dy", "0.32em")
    .attr("id", "timeLabel")
    .style("font-size", "2.5em")
    .style("font-weight", "bold")
    .style("fill", "white")
    .text(formatDate(keyFramesGlobal[0][0]));

  return ([date], transition) => {
    transition.end().then(() => now.text(formatDate(date)));
  };
}


////////////////////////////////////////////////////////////////
// Main

async function main() {

  data = await getData("/data.csv");
  names = getNames(data);
  const categories = getCategories(data);
  // const groupedData = groupData(data);

  const dateValues = getDataValues(data);
  keyFramesGlobal = getKeyFrames(dateValues);
  const nameFrames = getNameFrames(keyFramesGlobal);
  [prev, next] = getPrevNext(nameFrames);

  const svg = d3.select("#chart")
    .append("svg")
    .attr("viewBox", [0, 0, width, height]);

  const updateBars = drawBars(svg);
  const updateLabels = drawLabels(svg);
  const updateAxis = drawAxis(svg);
  const updateTicker = drawTicker(svg);

  // Add legend for categories' colors
  const legend = svg.append("g")
    .attr("transform", `translate(${width - 100}, ${height - 100})`);

  // legend.append("text")
  //   .attr("x", 0)
  //   .attr("y", 0)
  //   .attr("dy", "0.32em")
  //   .attr("id", "legendLabel")
  //   .text("Category");

  const getColorByCategory = (category) => {
    const scale = d3.scaleOrdinal(d3.schemeTableau10);
    scale.domain(Array.from(categories));
    return scale(category);
  }

  const legendItems = legend.selectAll("g")
    .data(categories)
    .join("g")
    .attr("transform", (d, i) => `translate(-10, ${i * 20})`);

  legendItems.append("rect")
    .attr("x", 0)
    .attr("y", -60)
    .attr("width", 10)
    .attr("height", 10)
    .attr("fill", d => getColorByCategory(d));

  legendItems.append("text")
    .attr("x", 20)
    .attr("y", -56)
    .attr("dy", "0.32em")
    .text(d => d)
    .style("fill", "grey")
    .style("font-size", "0.8em")
    .style("font-weight", "regular");



  for (const keyframe of keyFramesGlobal) {
    const transition = svg.transition()
      .duration(duration)
      .ease(d3.easeLinear);

    // Extract the top bar’s value.
    x.domain([0, keyframe[1][0].value]);

    updateAxis(keyframe, transition);
    updateBars(keyframe, transition);
    updateLabels(keyframe, transition);
    updateTicker(keyframe, transition);

    await transition.end();
  }


}

main();

