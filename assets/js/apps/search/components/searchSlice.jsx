import { createSlice } from '@reduxjs/toolkit';
import Cookies from 'js-cookie';
import { initialiseFilters, buildFilterQuery, updateFiltersByQuery } from "./filters/filterSlice";

const getResultFromHit = (hit,hitType,urlPrefix) => {
    const source = hit._source;
    source.type = hitType;
    source.url = `${urlPrefix}/${source.id}`;
    return source;
}

const getResultsFromResponse = (response) => {
// Grab the "_source" object out of each hit and also
// add a type attribute to them.
const hits = response.hits,
    projectResults = hits["projects"].map((hit) => {
        return getResultFromHit(hit,"project","/project/view")
    }),
    expResults = hits["experiments"].map((hit) => {
        return getResultFromHit(hit,"experiment","/experiment/view")
    }),
    dsResults = hits["datasets"].map((hit) => {
        return getResultFromHit(hit,"dataset","/dataset")
    }),
    dfResults = hits["datafiles"].map((hit) => {
        return getResultFromHit(hit,"datafile","/datafile/view")
    });
return {
    project: projectResults,
    experiment: expResults,
    dataset: dsResults,
    datafile: dfResults
}
}

/**
 * Selector for a type's current page size.
 * @param {*} searchSlice - The Redux state slice for search
 * @param {string} type -  MyTardis object type name.
 */
export const pageSizeSelector = (searchSlice, type) => {
    return searchSlice.pageSize[type];
};

/**
 * Selector for a type's current page number.
 * @param {*} searchSlice - The Redux state slice for search
 * @param {string} type - MyTardis object type name.
 */
export const pageNumberSelector = (searchSlice, type) => {
    return searchSlice.pageNumber[type];
};


const initialState = {
    searchTerm: null,
    isLoading: false,
    error:null,
    results:null,
    selectedType: "experiment",
    selectedResult: null,
    hideSensitive: true,
    pageSize: {
        projects: 50,
        experiments: 50,
        datasets: 50,
        datafiles: 50
    },
    pageNumber: {
        projects: 0,
        experiments: 0,
        datasets: 0,
        datafiles: 0
    }
};

const search = createSlice({
    name: 'search',
    initialState,
    reducers: {
        getResultsSuccess: {
            reducer: function (state, { payload }){
                state.results = payload;
                state.error = null;
                state.isLoading = false;
            },
            prepare: (rawResult) => {
                // Process the results first to extract hits and fill in URLs.
                return {
                    payload: getResultsFromResponse(rawResult)
                }
            }
        },
        updateSearchTerm: (state, {payload}) => {
            state.searchTerm = payload;
        },
        getResultsStart: (state) => {
            state.isLoading = true;
            state.error = null;
            state.selectedResult = null;
        },
        getResultsFailure: (state, {payload:error}) => {
            state.isLoading = false;
            state.error = error.toString();
            state.results = null;
        },
        updateSelectedType: (state,{payload: selectedType}) => {
            state.selectedType = selectedType;
            state.selectedResult = null;
        },
        updateSelectedResult: (state, {payload: selectedResult}) => {
            state.selectedResult = selectedResult;
        },
        updatePageSize: (state, {payload}) => {
            const { type, size } = payload;
            if (type) {
                state.pageSize[type] = size;
            } else {
                Object.keys(state.pageSize).forEach(typeName => {
                    state.pageSize[typeName] = size;
                });
            }
        },
        updatePageNumber: (state, {payload}) => {
            const { type, number } = payload;
            if (type) {
                state.pageNumber[type] = number;
            } else {
                Object.keys(state.pageNumber).forEach(typeName => {
                    state.pageNumber[typeName] = number;
                });
            }
        }
    }
});

const fetchSearchResults = (queryBody) => {
    return fetch(`/api/v1/search_simple-search/`,{
        method: 'post',
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': Cookies.get('csrftoken'),
        },
        body: JSON.stringify(queryBody)
    }).then(response => {
        if (!response.ok) {
            throw new Error("An error on the server occurred.")
        }
        return response.json()
    })
};


/**
 * Returns search API pagination query. 
 * @param {*} searchSlice - Redux search slice
 * @param {string} type If null, returns pagination for all types. If a MyTardis
 * type is specified, returns only pagination for that type.
 */
const buildPaginationQuery = (searchSlice, type) => {
    if (type) {
        return {
            offset: searchSlice.pageSize[type] * searchSlice.pageNumber[type],
            limit: searchSlice.pageSize[type]
        };
    } else {
        const offsets = Object.keys(searchSlice.pageSize).reduce((previous, objType) => {
            previous[objType] = searchSlice.pageSize[objType] * searchSlice.pageNumber[objType];
            return previous;
        }, {});
        return {
            offset: offsets,
            limit: searchSlice.pageSize
        };
    }
};

const buildQueryBody = (state, typeToSearch) => {
    const term = state.search.searchTerm,
        filters = buildFilterQuery(state.filters, typeToSearch),
        queryBody = {},
        pagination = buildPaginationQuery(state.search, typeToSearch);
    // Add pagination query
    Object.assign(queryBody, pagination);
    if (typeToSearch) {
        // If doing a single type search, include type in query body.
        queryBody.type = typeToSearch;
    }
    if (term !== null && term !== "") {
        queryBody.query = term;
    }
    if (filters !== null) {
        queryBody.filters = filters;
    }
    return queryBody;
};

const runSearchWithQuery = (queryBody) => {
    return (dispatch) => {
        dispatch(getResultsStart());
        return fetchSearchResults(queryBody)
            .then((results) => {
                dispatch(getResultsSuccess(results));
            }).catch((e) => {
                dispatch(getResultsFailure(e));
            });
    };
};

const getDisplayQueryString = (queryBody) => {
    // Determine how to show the query in the URL, depending on what's in the query body.
    const queryPrefix = "?q=";
    if (queryBody.filters) {
        // If the query contains filters, then use the stringified JSON format.
        return queryPrefix + JSON.stringify(queryBody);
    } else if (queryBody.query) {
        // If the query only has a search term, then just use the search term.
        return queryPrefix + queryBody.query;
    } else {
        // when there aren't any filters or search terms don't show a query at all.
        return location.pathname;
    }
}

const parseQuery = (searchString) => {
    // Find and return the query string or JSON body.
    if (searchString[0] === "?") {
        searchString = searchString.substring(1);
    }
    searchString = decodeURI(searchString);
    const parts = searchString.split('&');
    let queryPart = null;
    for (const partIdx in parts) {
        if (parts[partIdx].indexOf('q=') === 0) {
            queryPart = parts[partIdx].substring(2);
            break;
        }
    }
    if (!queryPart) { return {}; }
    try {
        return JSON.parse(queryPart);
    } catch (e) {
        // When we fail to parse, we assume it's a search term string.
        return { query: queryPart };
    }
}


const updateWithQuery = (queryBody) => {
    return (dispatch) => {
        dispatch(updateSearchTerm(queryBody.query));
        dispatch(updateFiltersByQuery(queryBody.filters));
    }
}


export const runSearch = () => {
    return (dispatch, getState) => {
        const state = getState();
        const queryBody = buildQueryBody(state);
        dispatch(runSearchWithQuery(queryBody));
        window.history.pushState(queryBody,"",getDisplayQueryString(queryBody));
    }
}

/**
 * An async reducer for running a single type search. This is usually
 * used for sort and pagination requests.
 * @param {string} typeToSearch - the MyTardis object type to run search on.
 */
export const runSingleTypeSearch = (typeToSearch) => {
    return (dispatch, getState) => {
        const state = getState();
        const queryBody = buildQueryBody(state, typeToSearch);
        dispatch(runSearchWithQuery(queryBody));
    }
}

export const restoreSearchFromHistory = (restoredState) => {
    return (dispatch) => {
        dispatch(runSearchWithQuery(restoredState));
        dispatch(updateWithQuery(restoredState));
    }
}


export const initialiseSearch = () => {
    return (dispatch, getState) => {
        const queryBody = parseQuery(window.location.search);
        window.history.replaceState(queryBody,"",getDisplayQueryString(queryBody));
        dispatch(runSearchWithQuery(queryBody));
        dispatch(initialiseFilters()).then(() => {
            if (!!queryBody) {
                dispatch(updateWithQuery(queryBody));
            }
        });
    }
}


export const {
    getResultsStart,
    getResultsSuccess,
    getResultsFailure,
    updateSearchTerm,
    updateSelectedType,
    updateSelectedResult
} = search.actions;

export default search.reducer;
