var d3 = require('d3')
var _ = require('underscore')
var svgPlots = require('./svgPlots')
var discogsData = require('../public/discogs.json')
var musicbrainzData = require('../public/musicbrainz.json')

// Pre-processing the data, turning maps into pairs, sorting by year
var _processData = function(seriesData) {
  delete seriesData.TOTAL
  return _.chain(seriesData).pairs().map(function(pair) {
      return [ parseInt(pair[0]), pair[1] ]
    }).sortBy(function(pair) {
      return pair[0]
    }).value()
}
discogsData = _processData(discogsData)
musicbrainzData = _processData(musicbrainzData)

// Plotting the estimated duration of music released per year
var yKey = 'duration_estimated'
var bounds = getBounds([ discogsData, musicbrainzData ], yKey)
var _processData = function(seriesData) {
  return _.map(seriesData, function(pair) {
    return {
      x: (pair[0] - bounds.minX) / (bounds.maxX - bounds.minX),
      y: (pair[1][yKey]) / bounds.maxY,
      label: [
        'YEAR : ' + pair[0],
        '' + Math.round((pair[1][yKey] / 1000000) * 1000) / 1000 + ' millions seconds released'
      ]
    }
  })
}

svgPlots.plotSeries(
  d3.select('svg#durationPerYear'), 
  [
    { seriesName: 'discogs', seriesData: _processData(discogsData) }, 
    { seriesName: 'musicbrainz', seriesData: _processData(musicbrainzData) }
  ], 
  [ '1990', '2014', '0 seconds', '' + Math.round(bounds.maxY) + ' seconds' ]
)

// Plotting the number of tracks released per year
var yKey = 'tracks_count'
var bounds = getBounds([ discogsData, musicbrainzData ], yKey)
var _processData = function(seriesData) {
  return _.map(seriesData, function(pair) {
    return {
      x: (pair[0] - bounds.minX) / (bounds.maxX - bounds.minX),
      y: (pair[1][yKey]) / bounds.maxY,
      label: [
        'YEAR : ' + pair[0],
        '' + pair[1][yKey] + ' tracks released'
      ]
    }
  })
}

svgPlots.plotSeries(
  d3.select('svg#tracksPerYear'), 
  [
    { seriesName: 'discogs', seriesData: _processData(discogsData) }, 
    { seriesName: 'musicbrainz', seriesData: _processData(musicbrainzData) }
  ], 
  [ '1990', '2014', '0 tracks', '' + bounds.maxY + ' tracks' ]
)

// UTILS
function getBounds(dataSources, yKey) {
  var minX = Infinity, maxX = 0
  var maxY = 0
  _.forEach(dataSources, function(seriesData) {
    maxX = Math.max(_.last(seriesData)[0], maxX)
    minX = Math.min(_.first(seriesData)[0], minX)
    maxY = Math.max(
      maxY, 
      _.chain(seriesData).pluck('1').pluck(yKey).max().value()
    )
  })
  return { minX: minX, maxX: maxX, maxY: maxY }
}