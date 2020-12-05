import requests
from requests.auth import HTTPBasicAuth
from random import randrange
import json
import config

# CONNECTION TO ELASTIC SEARCH

def callElastic(query):
    payload = ""
    rawData = requests.get(
        'https://66f07727639d4755971f5173fb60e420.europe-west3.gcp.cloud.es.io:9243/artworks/_search',
        auth=HTTPBasicAuth(config.userDcElastic, config.passDcElastic), params=payload, json=query)
    rawData.encoding = 'utf-8'
    dataDict = json.loads(rawData.text)
    return (dataDict)

# GET RANDOM OBJECT TYPES

def getRandomObjectTypes(requestedCountOfCollections):

    comparisonSets = config.depositary
    randomSetIndex = randrange(len(comparisonSets))
    selectedComparisonSet = comparisonSets[randomSetIndex]
    randomExhibition = []

    for collection in range(requestedCountOfCollections):
        randomCollectionIndex = randrange(len(selectedComparisonSet))
        if not selectedComparisonSet[randomCollectionIndex] in randomExhibition:
            randomExhibition.append(selectedComparisonSet[randomCollectionIndex])

    return randomExhibition

# PREPARING EXHIBITION QUERY
# Common properties for getArtworksByObject and getPeriodData

def exhibitionPropertiesQuery(dateFrom, dateTo):
    return [
        {
            "bool": {
                "should": [
                    {"match_phrase": {"work_type": "graphic"}},
                    {"match_phrase": {"work_type": "painting"}},
                    {"match_phrase": {"work_type": "drawing"}}
                ]
            }
        },
        {
            "range": {
                "date_latest": {
                    "gte": dateFrom,
                    "lt": dateTo
                }
            }
        }
    ]

# Common properties for getArtworksByObject query and getPeriodData aggregations
def prepareExhibitionKeywordQuery(exhibition):

    exhibitionKeywordsQuery = []

    # Adding match_phrase conditions to must query list. One for each object.
    exhibitionName = list(exhibition.keys())[0]
    exhibitionParams = exhibition[exhibitionName]
    for keywordsGroup in exhibitionParams:  # expanding exhibitionQuery from collection (exhibitionParams)
        keywordsQuery = []
        for keyword in keywordsGroup:  # expanding keywordsQuery from keywordsGroup
            keywordsQuery.append({"match_phrase": {"detected_objects.object": keyword}})
        exhibitionKeywordsQuery.append({"bool": {"should": keywordsQuery}})

    return exhibitionKeywordsQuery

# GET ARTWORKS BY OBJECT

def getArtworksByObject(exhibitionList, dateFrom, dateTo):

    allListsResult = []

    def sorter(artwork):
        score = artwork['_source']['average_score']
        return score

    for exhibition in exhibitionList:
        exhibitionKeywordsQuery = prepareExhibitionKeywordQuery(exhibition)
        exhibitionQuery = exhibitionPropertiesQuery(dateFrom, dateTo) + exhibitionKeywordsQuery

        # Only free artworks
        if config.onlyFreeArtworks == True:
            exhibitionQuery.append({"bool": {"must": [{"term": {"is_free": True}}]}})

        # Completing query
        requestForArtworks = {
            "size": 1000,
            "query": {
                "bool": {
                    "must": exhibitionQuery # includes above defined exhibitionQuery
                }
            },
            "aggs": {
                "periods": {
                    "histogram": {
                        "field": "date_latest",
                        "interval": 100
                    }
                }
            },
            "_source": {
                "includes": [
                    "_id",
                    "detected_objects.object",
                    "detected_objects.score",
                    "detected_objects.boundBox",
                    "title",
                    "author",
                    "gallery",
                    "date_earliest",
                    "date_latest"
                ]
            }
        }

        print('Request for artworks: ' + str(requestForArtworks))

        # Calling elastic database with completed query
        rawData = callElastic(requestForArtworks)
        artworks = rawData['hits']['hits']

        # expanding data by imageUrl and topObjectScore
        expandedArtworks = []

        for artwork in artworks:

            # generates image url
            imageUrl = 'https://storage.googleapis.com/digital-curator.appspot.com/artworks-all/' + artwork[
                '_id'] + '.jpg'  # Creating img url from artwork id
            artwork['_source']['image_url'] = imageUrl

            # rounds object score
            for object in artwork['_source']['detected_objects']:
                object['score'] = round(object['score'], 2)

            # selects searched object with highest score on image and saves it to topElementaryObjectScoreSum (It's useful for sorting)
            searchedObjectsScore = [] # saves highest probability achieved for each object
            #print('---next artwork---')
            exhibitionName = list(exhibition.keys())[0]
            for elementaryObjects in exhibition[exhibitionName]:

                for elementaryObject in elementaryObjects:

                    topElementaryObjectScore = 0
                    for detectedObject in artwork['_source']['detected_objects']:
                        if elementaryObject == detectedObject['object'] and detectedObject['score'] >= topElementaryObjectScore: # If it searched elementaryObject and if is higher than topElementaryObjectScore
                            topElementaryObjectScore = detectedObject['score']

                    searchedObjectsScore.append(topElementaryObjectScore)
                    #print(elementaryObject, topElementaryObjectScore)

            artwork['_source']['searched_object'] = exhibitionName
            artwork['_source']['average_score'] = round(sum(searchedObjectsScore) / len(searchedObjectsScore), 2) # get percents
            expandedArtworks.append(artwork)

        # sorts expandedArtworks by topObjectScore
        sortedArtworks = sorted(expandedArtworks, key=sorter, reverse=True)[:config.maxGallerySize]
        allListsResult.append(sortedArtworks)

    return allListsResult

# AGGREGATIONS BY PERIODS

def getPeriodData(exhibitionsList, interval, dateFrom, dateTo):

    # preparing object filters for query
    aggregations = {}
    def prepareQuery(exhibitionsList):
        counter = 1
        for exhibition in exhibitionsList:
            exhibitionQuery = prepareExhibitionKeywordQuery(exhibition)
            groupAggregation = {
                "filter": {
                    "bool": {
                        "must": exhibitionQuery
                    }
                }
            }
            exhibitionName = list(exhibition.keys())[0]
            aggregations[exhibitionName] = groupAggregation
            counter +=1

    prepareQuery(exhibitionsList)

    # completing query
    requestForPeriodData = {
        "size": 0,
        "query": {
            "bool": {
                "must": exhibitionPropertiesQuery(dateFrom,dateTo)
            }
        },
        "aggs": {
            "periods": {
                "aggs": aggregations
                ,
                "histogram": {
                    "field": "date_latest",
                    "interval": interval
                }
            }
        }
    }
    print('Request for periods data: ' + str(requestForPeriodData))
    countAll = callElastic(requestForPeriodData)['aggregations']['periods']['buckets'] # Gets count of all artworks in specific periods

    relatedPeriods = []
    for periodSet in countAll: # Gets labels
        if periodSet['doc_count'] > config.minArtworksLimit or len(relatedPeriods) > 0: # cuts periods with small number of artworks but only from beginning of timeline
            relatedPeriods.append(periodSet['key'])

    totalArtworks = [periodSet['doc_count'] for periodSet in countAll if periodSet['key'] in relatedPeriods] # check if period is in relatedPeriods and if so, it adds count to totoal artworks

    artworksInPeriod = {'periods': relatedPeriods, 'totalArtworks': totalArtworks, 'artworksWithObject': []}

    for object in exhibitionsList:
        objectName = list(object.keys())[0]
        artworksWithObject = [periodSet[objectName]['doc_count'] for periodSet in countAll if periodSet['key'] in relatedPeriods]  # check if period is in relatedPeriods and if so, it adds count to related artworks
        objectPercents = []
        for item in range(len(totalArtworks)):
            if totalArtworks[item] == 0: # Eliminates dividing by zero error
                objectPercents.append(0)
            else:
                objectPercents.append(round(artworksWithObject[item] / totalArtworks[item], 3) * 100)  # Counting percent of artworks copntained selected object in comparison with total artworks
        artworksInPeriod['artworksWithObject'].append([objectName, artworksWithObject, objectPercents])

    return artworksInPeriod

# GET COLLECTION SUM

def getGalleriesSum():
    collectionsQuery = {
        "size": 0,
        "aggs": {
            "galleries_sum": {
                "terms": {
                    "field": "gallery.keyword",
                    "size": 1000
                },
            },
            "free_sum": {
                "terms": {
                    "field": "is_free"
                }
            }
        }
    }
    rawData = callElastic(collectionsQuery)['aggregations']
    galleriesData = rawData['galleries_sum']['buckets']
    freeArtworksCount = rawData['free_sum']['buckets'][1]['doc_count']
    galleriesCount = len(galleriesData)
    artworksCount = 0
    for gallery in galleriesData:
        artworksCount += gallery['doc_count']
    summary = {'galleries count': galleriesCount, 'artworks count': artworksCount, 'free artworks count': freeArtworksCount}
    return summary

# GET DETECTED OBJECT LIST

def getDetectedObjectsList():
    collectionsQuery = {
        "size":0,
        "aggs" : {
            "detected_objects_list" : {
                "terms" : {
                    "field" : "detected_objects.object.keyword",
                    "size": 10000
                }
            }
        }
    }
    DetectedObjectClassesList = callElastic(collectionsQuery)['aggregations']['detected_objects_list']['buckets']
    TuplesClassesList = []
    for objectClass in DetectedObjectClassesList:
        TuplesClassesList.append((objectClass['key'],objectClass['key']+' '+str(objectClass['doc_count'])))
    return TuplesClassesList

# DEVIDE EVERY COLLECTION BY PERIODS AND SORTS ARTWORKS INTO SPECIFIC PERIOD BY ITS DATE EARLIEST
def devideCollectionByPeriods(objectsByPeriods, getArtworksByObject):
    sortedCollections = []

    for collection in getArtworksByObject:
        collectionPeriodsList = []

        for period in objectsByPeriods['periods']:
            periodStart = int(period)
            periodEnd = int(periodStart) + config.periodLength
            periodName = str(periodStart) +' - '+ str(periodEnd)
            periodArtworksList = []

            for artwork in collection:
                artworkDatation = artwork['_source']['date_earliest']
                if artworkDatation >= periodStart and artworkDatation < periodEnd:
                    periodArtworksList.append(artwork)

            if len(periodArtworksList) > 0:
                collectionPeriod = {periodName: periodArtworksList}
                collectionPeriodsList.append(collectionPeriod)

        sortedCollections.append(collectionPeriodsList)

    return sortedCollections



#print(getDetectedObjectsList())
#getArtworksByObject(config.exhibitionsList)
#getPeriodData(config.exhibitionsList,100, config.dateFrom, config.dateTo)
#print(getRandomObjectTypes(3))
#print(getGalleriesSum())


