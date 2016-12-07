var d3 = require('d3')
var _ = require('underscore')

exports.plotSeries = function(svgElem, dataSources, axisLabels) {
  var svgWidth = 1000
  var svgHeight = 600
  var paddingX = paddingY = 60
  var paddingAxis = 90
  var labelPaddingX = labelPaddingY = 20
  var circleR = 8

  svgElem.attr('viewBox', '0 0 ' + svgWidth + ' ' + svgHeight + '')

  // Draw axis and axis labels
  var _drawAxis = function(points) {
    svgElem.append('path')
      .attr('class', 'axis')
      .attr('d', d3.line()(points))
  }
  _drawAxis([[ paddingX + paddingAxis, paddingY ], 
    [ svgWidth - (paddingX + paddingAxis), paddingY ]])
  _drawAxis([[ svgWidth - paddingX, paddingY + paddingAxis ], 
    [ svgWidth - paddingX, svgHeight - (paddingY + paddingAxis) ]])
  _drawAxis([[ paddingX + paddingAxis, svgHeight - paddingY ], 
    [ svgWidth - (paddingX + paddingAxis), svgHeight - paddingY ]])
  _drawAxis([[ paddingX, paddingY + paddingAxis ], 
    [ paddingX, svgHeight - (paddingY + paddingAxis) ]])

  var _drawAxisLabel = function(label, x, y, angle) {
    return svgElem.append('g')
      .attr('class', 'axisLabel')
      .attr('transform', 'translate(' + x + ' ' + y + ')')
      .append('text')
        .attr('transform', 'rotate(' + angle + ')')
        .attr('text-anchor', 'middle')
        .attr('alignment-baseline', 'middle')
        .text(label)
  }
  _drawAxisLabel(axisLabels[0], paddingX / 2, svgHeight / 2, -90)
  _drawAxisLabel(axisLabels[1], svgWidth - paddingX / 2, svgHeight / 2, -90)
  _drawAxisLabel(axisLabels[2], svgWidth / 2, svgHeight - paddingY / 2, 0)
  _drawAxisLabel(axisLabels[3], svgWidth / 2, paddingY / 2, 0)


  svgElem.selectAll('.dataSource')
    .data(dataSources).enter().append('g')
    .attr('class', function(dataSource) { return 'dataSource ' + dataSource.seriesName })
    .each(function(dataSource) {
      var points = dataSource.seriesData
      _.forEach(points, function(point) {
        point.x = paddingX + point.x * (svgWidth - 2 * paddingX)
        point.y = (svgHeight - paddingY) - (svgHeight - 2 * paddingY) * point.y
      })

      // Add data series name
      d3.select(this)
        .append('text')
        .attr('transform', 'translate(' + _.last(points).x + ' ' + _.last(points).y + ')')
        .attr('text-anchor', 'middle')
        .attr('alignment-baseline', 'middle')
        .attr('dy', '1.2em')
        .text(dataSource.seriesName)

      // Append curve path
      var lineFunction = d3.line()
        .x(function(point) { return point.x })
        .y(function(point) { return point.y })
        .curve(d3.curveLinear)

      d3.select(this).append('path')
        .attr('class', 'curve')
        .attr('d', lineFunction(points))
        .attr('fill', 'none')

      // Append points and tooltips
      var valueGroup = d3.select(this).selectAll('g.value')
        .data(points).enter().append('g').attr('class', 'value')
        .attr('transform', function(point) { return 'translate(' + point.x + ' ' + point.y + ')' })
        .on('mouseover', _addTooltip)
        .on('mouseout', function() { 
          d3.selectAll('g.tooltip').remove() 
        })

      valueGroup
        .append('circle')
        .attr('cx', 0).attr('cy', 0).attr('r', circleR)

      function _addTooltip(point) {
        var tooltipContainer = svgElem.append('g')
          .attr('transform', 'translate(' + point.x + ' ' + point.y + ')')
          .attr('class', 'tooltip ' + dataSource.seriesName)
        var tooltip = tooltipContainer.append('g')

        var label = tooltip
          .append('text')
          .attr('class', 'label')

        _.forEach(point.label, function(str, i) {
          label.append('tspan')
            .attr('x', 0)
            .attr('dy', '' + i + 'em')
            .text('' + str)
        })

        // Add background
        var bbox = tooltip.node().getBBox()
        tooltip
          .insert('rect', ':first-child')
          .attr('class', 'bg')
          .attr('width', bbox.width + 2 * labelPaddingX)
          .attr('height', bbox.height + 2 * labelPaddingY)
          .attr('y', '-1em')
          .attr('transform', 'translate(' + -labelPaddingX + ' ' + -labelPaddingY + ')')

        var spaceX
        if (point.x >= svgWidth / 2) {
          spaceX = -((tooltip.node().getBBox().width) - 15)
        } else { 
          spaceX = (circleR + labelPaddingX)
        }
        // Add a bit of space to show the tooltip on the side of the data point
        tooltip.attr('transform', 'translate(' + spaceX + ' 0)')
      }
    })
}