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
    results = {};
    if (hits.projects) {
        results.projects = hits.projects.map((hit) => {
            return getResultFromHit(hit,"project","/project/view")
        });
    }
    if (hits.experiments) {
        results.experiments = hits.experiments.map((hit) => {
            return getResultFromHit(hit,"experiment","/experiment/view")
        });
    }
    if (hits.datasets) {
        results.datasets = hits.datasets.map((hit) => {
            return getResultFromHit(hit,"dataset","/dataset")
        });
    }
    if (hits.datafiles) {
        results.datafiles = hits["datafiles"].map((hit) => {
            return getResultFromHit(hit,"datafile","/datafile/view")
        });
    }
    return results;
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

export const totalHitsSelector = (searchSlice, typeId) => (
    searchSlice.results ? searchSlice.results.totalHits[typeId + "s"] : 0
);

/**
 * Returns the index of the first item on the current page. For example,
 * if we are on the second page, and each page has 20 items, then this function
 * returns 21.
 * @param {*} searchSlice The Redux state slice for search
 * @param {string} typeId MyTardis object type name.
 */
export const pageFirstItemIndexSelector = (searchSlice, typeId) => {
    if (totalHitsSelector(searchSlice, typeId) === 0) {
        return 0;
    } else {
        return pageSizeSelector(searchSlice, typeId) * (pageNumberSelector(searchSlice, typeId) - 1) + 1;
    }
}

/**
 * Selector for the total number of pages of results for a particular type.
 * @param {*} searchSlice - The Redux state slice for search
 * @param {string} typeId - The MyTardis object type. NOTE that this selector expects the type name in its singular form.
 */
export const totalPagesSelector = (searchSlice, typeId) => (
    Math.ceil(totalHitsSelector(searchSlice, typeId) / pageSizeSelector(searchSlice, typeId))
);

const initialState = {
    searchTerm: null,
    isLoading: false,
    error:null,
    results:null,
    selectedType: "experiment",
    selectedResult: null,
    hideSensitive: true,
    pageSize: {
        project: 20,
        experiment: 20,
        dataset: 20,
        datafile: 20
    },
    pageNumber: {
        project: 1,
        experiment: 1,
        dataset: 1,
        datafile: 1
    },
    showSensitiveData: false
};

const search = createSlice({
    name: 'search',
    initialState,
    reducers: {
        getResultsSuccess: {
            reducer: function (state, { payload }) {
                if (state.results && state.results.hits) {
                    // If there are already results, do a merge in case
                    // this was a single type query.
                    Object.assign(state.results.hits, payload.hits);
                    Object.assign(state.results.totalHits, payload.totalHits);
                } else {
                    state.results = payload;
                }
                state.error = null;
                state.isLoading = false;
            },
            prepare: (rawResult) => {
                // Process the results first to extract hits and fill in URLs.
                return {
                    payload: {
                        hits: getResultsFromResponse(rawResult),
                        totalHits: rawResult.total_hits
                    }
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
            const { typeId, size } = payload;
            if (typeId) {
                state.pageSize[typeId] = size;
            } else {
                Object.keys(state.pageSize).forEach(typeName => {
                    state.pageSize[typeName] = size;
                });
            }
        },
        updatePageNumber: (state, {payload}) => {
            const { typeId, number } = payload;
            if (typeId) {
                state.pageNumber[typeId] = number;
            } else {
                Object.keys(state.pageNumber).forEach(typeName => {
                    state.pageNumber[typeName] = number;
                });
            }
        },
        resetPageNumber: (state) => {
            // Reset page count.
            state.pageNumber = initialState.pageNumber;
        },
        toggleShowSensitiveData: (state) => {
            state.showSensitiveData = !state.showSensitiveData;
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
            offset: pageSizeSelector(searchSlice, type) * (pageNumberSelector(searchSlice, type) - 1),
            size: pageSizeSelector(searchSlice, type)
        };
    } else {
        const offsets = Object.keys(searchSlice.pageSize).reduce((previous, objType) => {
            previous[objType] = searchSlice.pageSize[objType] * (searchSlice.pageNumber[objType] - 1);
            return previous;
        }, {});
        return {
            offset: offsets,
            size: searchSlice.pageSize
        };
    }
};

const buildQueryBody = (state, typeToSearch) => {
    const term = state.search.searchTerm,
        filters = buildFilterQuery(state.filters, typeToSearch),
        queryBody = {};

    if (typeToSearch) {
        // If doing a single type search, include type in query body.
        queryBody.type = typeToSearch;
        // Add pagination query
        Object.assign(queryBody, buildPaginationQuery(state.search, typeToSearch));
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
        dispatch(search.actions.resetPageNumber());
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

export const updatePageNumberAndRefetch = (typeId, number) => {
    return (dispatch, getState) => {
        const state = getState();
        const totalPages = totalPagesSelector(state.search, typeId);
        if (number < 1 || number > totalPages) {
            return;
        }
        dispatch(search.actions.updatePageNumber({typeId, number}));
        return dispatch(runSingleTypeSearch(typeId));
    };
};

export const updatePageSizeAndRefetch = (typeId, size) => {
    return (dispatch, getState) => {
        const state = getState();
        // Calculate new page number
        const currentFirstItem = pageFirstItemIndexSelector(state.search, typeId);
        const newPageNumber = Math.ceil(currentFirstItem / size);
        dispatch(search.actions.updatePageSize({typeId, size}));
        dispatch(search.actions.updatePageNumber({typeId, number: newPageNumber}));
        return dispatch(runSingleTypeSearch(typeId));
    };
};

export const {
    getResultsStart,
    getResultsSuccess,
    getResultsFailure,
    updateSearchTerm,
    updateSelectedType,
    updateSelectedResult,
    toggleShowSensitiveData
} = search.actions;

export default search.reducer;
