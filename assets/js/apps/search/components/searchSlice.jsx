import { createSlice } from "@reduxjs/toolkit";
import Cookies from "js-cookie";
import { batch } from "react-redux";
import { initialiseFilters, buildFilterQuery, updateFiltersByQuery, typeSelector } from "./filters/filterSlice";

const getResultsFromResponse = (response) => {
    const getTypeResultsFromResponse = (type, hitsForType) => {
        // Grab the "_source" object out of each hit for this type and also
        // add a type attribute to them.    
        const resultsForType = {
            byId: {},
            allIds: []
        };
        hitsForType.forEach(hit => {
            // eslint-disable-next-line no-underscore-dangle
            const source = hit._source;
            resultsForType.allIds.push(source.id);
            source.type = type;
            source.url = `/${type}/view/${source.id}`;    
            resultsForType.byId[source.id] = source;
        });
        return resultsForType;
    };
    const hits = response.hits;
    const results = {};
    if (hits.project) {
        results.project = getTypeResultsFromResponse("project", hits.project);
    }
    if (hits.experiment) {
        results.experiment = getTypeResultsFromResponse("experiment", hits.experiment);
    }
    if (hits.dataset) {
        results.dataset = getTypeResultsFromResponse("dataset", hits.dataset);
    }
    if (hits.datafile) {
        results.datafile = getTypeResultsFromResponse("datafile", hits.datafile);
    }
    return results;
};

/**
 * Process JSON results from search API and return the results.
 * @private
 * @param {object} response JSON result from search API endpoint. 
 */
function getHitTotalsFromResponse(response) {
    const hitTotals = response.total_hits;
    const results = {};
    if (hitTotals.project !== undefined) {
        results.project = hitTotals.project;
    }
    if (hitTotals.experiment !== undefined) {
        results.experiment = hitTotals.experiment;
    }
    if (hitTotals.dataset !== undefined) {
        results.dataset = hitTotals.dataset;
    }
    if (hitTotals.datafile !== undefined) {
        results.datafile = hitTotals.datafile;
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
    searchSlice.results ? searchSlice.results.totalHits[typeId] : 0
);

export const SORT_ORDER = {
    ascending: "asc",
    descending: "desc"
};

export const SELECTION_STATE = {
    None: "NONE",
    Some: "SOME",
    Page: "PAGE",
    All: "ALL"
};

/**
 * Selector for sorts that are active on a typeId.
 * @param {*} searchSlice The Redux state slice for search
 * @param {string} typeId MyTardis object type.
 */
export const activeSortSelector = (searchSlice, typeId) => (
    searchSlice.sort[typeId].active
);

/**
 * Selector for type attributes which are sortable.
 * @param {*} filterSlice Redux state slice for filters
 * @param {string} typeId MyTardis object type.
 */
export const sortableAttributesSelector = (filterSlice, typeId) => {
    const typeAttributes = typeSelector(filterSlice, typeId).attributes;
    return typeAttributes.allIds.map(attributeId => (
        typeAttributes.byId[attributeId]
    )).filter(attribute => attribute.sortable);
};

/**
 * Selector for the sort order of an attribute.
 * @param {*} searchSlice Redux state slice for search
 * @param {string} typeId MyTardis object type
 * @param {string} attributeId Attribute ID
 */
export const sortOrderSelector = (searchSlice, typeId, attributeId) => (
    searchSlice.sort[typeId].order[attributeId] || SORT_ORDER.ascending
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
};

/**
 * Selector for the total number of pages of results for a particular type.
 * @param {*} searchSlice - The Redux state slice for search
 * @param {string} typeId - The MyTardis object type. NOTE that this selector expects the type name in its singular form.
 */
export const totalPagesSelector = (searchSlice, typeId) => (
    Math.ceil(totalHitsSelector(searchSlice, typeId) / pageSizeSelector(searchSlice, typeId))
);

/**
 * Selector for the search term, if any, for a particular type.
 * @param {string} typeId MyTardis object type.
 */
export const searchTermSelector = (searchSlice, typeId) => (
    // Check search term exists and is an object before returning
    // search term.
    (searchSlice &&
        searchSlice.searchTerm &&
        typeof searchSlice.searchTerm === "object" &&
        !Array.isArray(searchSlice.searchTerm))
        ?
        searchSlice.searchTerm[typeId] : ""
);

/**
 * Return a list of selected items.
 * @param {Object} searchSlice Redux search slice object.
 * @param {String} typeId ID for object type
 */
export const getSelectedItems = (searchSlice, typeId) => {
    if (!searchSlice.results) {
        return [];
    }
    // Grab all selected items
    return Object
        .keys(searchSlice.selected[typeId].items)
        .map(id => ({typeId, id: parseInt(id)}));
};

const initialState = {
    searchTerm: {},
    isLoading: false,
    error: null,
    results: null,
    selectedType: "experiment",
    highlightedResult: null,
    selected: {
        project: {
            selectionState: SELECTION_STATE.None,
            items: {}
        },
        experiment: {
            selectionState: SELECTION_STATE.None,
            items: {}
        },
        dataset: {
            selectionState: SELECTION_STATE.None,
            items: {}
        },
        datafile: {
            selectionState: SELECTION_STATE.None,
            items: {}
        }
    },
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
    sort: {
        project: {
            active: [],
            order: {}
        },
        experiment: {
            active: [],
            order: {}
        },
        dataset: {
            active: [],
            order: {}
        },
        datafile: {
            active: [],
            order: {}
        }
    },
    showSensitiveData: false
};

const search = createSlice({
    name: "search",
    initialState,
    reducers: {
        getResultsSuccess: {
            reducer: function(state, { payload }) {
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
            prepare: rawResult => {
                // Process the results first to extract hits and fill in URLs.
                return {
                    payload: {
                        hits: getResultsFromResponse(rawResult),
                        totalHits: getHitTotalsFromResponse(rawResult)
                    }
                };   
            }
        },
        updateSearchTerm: (state, {payload}) => {
            const {searchTerm = {}, replaceState = false} = payload;
            if (replaceState) {
                // If replaceState is set, then replace
                // state as a whole rather than update
                // specified search terms.
                state.searchTerm = searchTerm;
            } else {
                const currentSearchTerm = state.searchTerm || {};
                state.searchTerm = Object.assign(currentSearchTerm, searchTerm);
            }
            // Clean up empty string search terms
            Object.keys(state.searchTerm).forEach(type => {
                if (state.searchTerm[type] === "") {
                    delete state.searchTerm[type];
                }
            });
            // Finally, if there are no search terms, delete
            // the empty object.
            if (Object.keys(state.searchTerm).length === 0) {
                state.searchTerm = undefined;
            }
        },
        toggleItemSelected: (state, {payload}) => {
            const {typeId, id} = payload;
            const typeSelectedResults = state.selected[typeId].items;
            if (!typeSelectedResults[id]) {
                typeSelectedResults[id] = "selected";
            } else {
                delete typeSelectedResults[id];
            }
            if (Object.keys(typeSelectedResults).length > 0) {
                state.selected[typeId].selectionState = SELECTION_STATE.Some;
            } else {
                state.selected[typeId].selectionState = SELECTION_STATE.None;
            }
        },
        deselectAllItems: (state, {payload}) => {
            const {typeId} = payload;
            state.selected[typeId].items = initialState.selected[typeId].items;
            state.selected[typeId].selectionState = SELECTION_STATE.None;
        },
        selectAllItems: (state, {payload}) => {
            // Select multiple items in results of the same type.
            const {typeId, itemIds} = payload;
            itemIds.forEach(id => {
                state.selected[typeId].items[id] = "selected";
            });
            state.selected[typeId].selectionState = SELECTION_STATE.All;
        },
        selectPageItems: (state, {payload}) => {
            // Select multiple items in results of the same type.
            const {typeId} = payload;
            const itemIds = state.results.hits[typeId].allIds;
            itemIds.forEach(id => {
                state.selected[typeId].items[id] = "selected";
            });
            state.selected[typeId].selectionState = SELECTION_STATE.Page;
        },
        getResultsStart: (state) => {
            state.isLoading = true;
            state.error = null;
            state.highlightedResult = null;
        },
        getResultsFailure: (state, {payload: error}) => {
            state.isLoading = false;
            state.error = error;
            state.results = null;
        },
        updateSelectedType: (state, {payload: selectedType}) => {
            state.selectedType = selectedType;
            state.highlightedResult = null;
        },
        updateHighlightedResult: (state, {payload: highlightedResult}) => {
            state.highlightedResult = highlightedResult;
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
        },
        updateResultSort: (state, {payload}) => {
            const { typeId, attributeId, order = SORT_ORDER.ascending } = payload;
            state.sort[typeId].order[attributeId] = order;
            // Update sort order.
            const existingSort = state.sort[typeId].active.filter(
                sort => sort === attributeId
            );
            if (existingSort.length === 0) {
                // Add new sort
                state.sort[typeId].active.push(attributeId);
            }
        },
        removeResultSort: (state, {payload}) => {
            const { typeId, attributeId } = payload;
            const typeSorts = activeSortSelector(state, typeId);
            for (let i = 0; i < typeSorts.length; i++) {
                if (typeSorts[i] === attributeId) {
                    // Remove the sort.
                    typeSorts.splice(i, 1);
                    return;
                }
            }
        }
    }
});

export const {
    getResultsStart,
    getResultsSuccess,
    getResultsFailure,
    updateSearchTerm,
    updateSelectedType,
    updateHighlightedResult,
    toggleShowSensitiveData,
    updateResultSort,
    removeResultSort,
    toggleItemSelected,
    selectPageItems,
    deselectAllItems,
} = search.actions;


const fetchSearchResults = (queryBody) => {
    return fetch(`/api/v1/search_simple-search/`, {
        method: "post",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": Cookies.get("csrftoken"),
        },
        body: JSON.stringify(queryBody)
    }).then(response => {
        if (!response.ok) {
            throw response;
        }
        return response.json();
    }, rejectedError => {
        throw rejectedError.message;
    });
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

/**
 * Returns search API sort query.
 * @param {*} state The overall Redux state tree
 * @param {string} typeToSearch Type ID to search. If null, assume all types are searched for.
 */
const buildSortQuery = (state, typeToSearch) => {
    const typesToSort = typeToSearch ? [typeToSearch] : ["project", "experiment", "dataset", "datafile"];
    const sortQuery = typesToSort.reduce((acc, typeId) => {
        const sortOptions = activeSortSelector(state.search, typeId);
        const typeSortQuery = sortOptions.map(id => {
            const order = state.search.sort[typeId].order[id];
            const attribute = typeSelector(state.filters, typeId).attributes.byId[id];
            const fullField = [id].concat(attribute.nested_target || []);
            return {
                field: fullField,
                order
            };
        });
        if (typeSortQuery.length !== 0) {
            acc[typeId] = typeSortQuery;
        }
        return acc;
    }, {});
    if (Object.keys(sortQuery).length === 0) {
        return null;
    }
    return {
        sort: sortQuery
    };
};

const buildQueryBody = (state, typeToSearch, shouldApplySortPagination = true) => {
    const term = state.search.searchTerm,
        filters = buildFilterQuery(state.filters, typeToSearch),
        queryBody = {};

    // Add sort query
    if (shouldApplySortPagination) {
        Object.assign(queryBody, buildSortQuery(state, typeToSearch));
    }
    if (typeToSearch) {
        // If doing a single type search, include type in query body.
        queryBody.type = typeToSearch;
        // Add pagination query
        if (shouldApplySortPagination) {
            Object.assign(queryBody, buildPaginationQuery(state.search, typeToSearch));
        }
    }
    if (term !== null) {
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
            }).catch((error) => {
                if (error &&
                    !isNaN(error.status)) {
                    // If error occurred on the endpoint, we check the status code first.
                    if (error.status === 401) {
                        // We made an Unauthorized request!
                        // Redirect to log in first, and then do search.
                        location.replace("/login/?next=/app/search");
                    } else {
                        error = error.statusText;
                    }
                }
                dispatch(getResultsFailure(error));
            });
    };
};

const getDisplayQueryString = (queryBody) => {
    // Determine how to show the query in the URL, depending on what's in the query body.
    if (queryBody.filters || (queryBody.query && Object.keys(queryBody.query).length > 0 )) {
        // If the query contains filters, then use the stringified JSON format.
        return "?q=" + encodeURIComponent(JSON.stringify(queryBody));
    } else {
        // when there aren't any filters or search terms don't show a query at all.
        return location.pathname;
    }
};

/**
 * Selector for whether there are any active quick search terms.
 * @param {*} searchSlice Redux search slice
 */
export const hasActiveSearchTermSelector = searchSlice => {
    // Then look through whether there are any quick search terms.
    return Object.keys(searchSlice.searchTerm || {}).length > 0;
};


/**
 * Given the search part of URL, returns the search term or filters serialised in there.
 * @param {string} searchString The search part of URL.
 * @private Only exported to run unit tests
 */
export const parseQuery = (searchString) => {
    const convertLegacySearchTermQuery = (searchTerm) => {
        // Convert text string search term queries
        // to new format if so.
        if (!searchTerm) {
            return {};
        }
        return {
            query: {
                project: searchTerm,
                experiment: searchTerm,
                dataset: searchTerm,
                datafile: searchTerm
            }
        };
    };

    const buildResultForParsedQuery = (queryString) => {
        if (!queryString) { return {}; }
        try {
            const parsed = JSON.parse(queryString);
            if (typeof parsed === "object" && !Array.isArray(parsed)) {
                return parsed;
            } else {
                return convertLegacySearchTermQuery(queryString);
            }
        } catch (e) {
            // When we fail to parse, we assume it's a search term string.
            return convertLegacySearchTermQuery(queryString);
        }
    };


    // Find and return the query string or JSON body.
    if (searchString[0] === "?") {
        searchString = searchString.substring(1);
    }
    searchString = decodeURIComponent(searchString);
    const parts = searchString.split("&");
    let queryPart = null;
    for (const partIdx in parts) {
        if (parts[partIdx].indexOf("q=") === 0) {
            queryPart = parts[partIdx].substring(2);
            break;
        }
    }
    return buildResultForParsedQuery(queryPart);
};

/**
 * An async reducer for updating the Redux state tree from saved state.
 * @param {object} queryBody the serialised query body
 */
const updateWithQuery = (queryBody) => {
    return (dispatch) => {
        batch(() => {
            dispatch(updateSearchTerm({
                searchTerm: queryBody.query,
                replaceState: true
            }));
            dispatch(updateFiltersByQuery(queryBody.filters));
        });
    };
};


export const runSearch = () => {
    return (dispatch, getState) => {
        const state = getState();
        const queryBody = buildQueryBody(state);
        dispatch(runSearchWithQuery(queryBody));
        dispatch(search.actions.resetPageNumber());
        window.history.pushState(queryBody, "", getDisplayQueryString(queryBody));
    };
};

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
    };
};

export const restoreSearchFromHistory = (restoredState) => {
    return (dispatch) => {
        dispatch(runSearchWithQuery(restoredState));
        dispatch(updateWithQuery(restoredState));
    };
};

export const initialiseSearch = () => {
    return (dispatch, getState) => {
        const queryBody = parseQuery(window.location.search);
        window.history.replaceState(queryBody, "", getDisplayQueryString(queryBody));
        dispatch(runSearchWithQuery(queryBody));
        dispatch(initialiseFilters()).then(() => {
            if (queryBody) {
                dispatch(updateWithQuery(queryBody));
            }
        });
    };
};

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

/**
 * Fetches a list of all MyTardis objects of type typeId
 * that match the current query, then select them. This
 * action is to support the "Select All" button in the 
 * search UI.
 * @param {String} typeId 
 * @returns A Promise that is resolved when the list of item IDs is fetched
 * and dispatched to the Redux store.
 */
export const selectAllTypeItems = typeId => {
    return (dispatch, getState) => {
        const state = getState();
        const queryBody = buildQueryBody(state, typeId, false);
        return fetchSearchResults(queryBody).then(response => {
            const itemIds = getResultsFromResponse(response)[typeId].allIds;
            return dispatch(search.actions.selectAllItems({
                typeId,
                itemIds
            }));
        });
        
    };
};

export default search.reducer;
