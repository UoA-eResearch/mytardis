import { createSlice } from "@reduxjs/toolkit";
import localforage from "localforage";
import mockCartData from "./mock-cart.json";
import Cookies from "js-cookie";

export const LOADING_STATE = {
    Initial: "INITIAL",
    LoadingFromCache: "LOADING",
    Validating: "VALIDATING",
    Finished: "FINISHED",
    Error: "ERROR"
};

export const NOTIFICATION_TYPE = {
    ItemsRemoved: "REMOVED",
    ItemsAdded: "ADDED"
};

const initialState = {
    itemsInCart: {
        allIds: [],
        byId: {}
    },
    status: LOADING_STATE.Initial,
    objects: {
        allIds: [],
        byId: {}
    },
    activeNotification: null
};

const cartSlice = createSlice({
    name: "cart",
    initialState,
    reducers: {
        itemsIsLoading: (state) => {
            state.status = LOADING_STATE.LoadingFromCache;
        },
        itemRemoved: (state, {payload}) => {
            const { typeId, id } = payload;
            const itemsByType = state.itemsInCart;
            if (!itemsByType.byId || !itemsByType.byId[typeId] || itemsByType.byId[typeId][id]) {
                return;
            }
            // Remove the deleted item ID. 
            itemsByType.byId[typeId] = itemsByType.byId[typeId].filter(itemId => itemId !== id);
            if (itemsByType.byId[typeId].length === 0) {
                delete itemsByType.byId[typeId];
                itemsByType.allIds = itemsByType.allIds.filter(listTypeId => listTypeId !== typeId);
            }
            state.activeNotification = NOTIFICATION_TYPE.ItemsRemoved;
        },
        notificationDismissed: (state) => {
            state.activeNotification = null;
        },
        cartLoaded: (state, {payload}) => {
            const {itemIdsByType, items} = payload;
            if (itemIdsByType) {
                state.itemsInCart = itemIdsByType;
            }
            if (items) {
                state.objects = items;
            }
            state.status = LOADING_STATE.Finished;
        },
        objectsValidating: (state, {payload}) => {
            state.status = LOADING_STATE.Validating;
        },
        objectsValidated: (state, {payload}) => {
            state.objects = payload;
            state.status = LOADING_STATE.Finished;
        },
        objectsValidationFailed: state => {
            state.status = LOADING_STATE.Error;
        },
        
        // removeItem: (state, {payload}) => {
        //     const {typeId, id} = payload;
            
        // }
    }
});

export const {
    itemsIsLoading,
    itemRemoved,
    cartLoaded,
    objectsValidating,
    objectsValidated,
    itemsLoadFailed,
    notificationDismissed
} = cartSlice.actions;

const fetchObjectById = (typeId, id) => {
    return fetch(`/api/v1/${typeId}/${id}/`, {
        method: "get",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": Cookies.get("csrftoken"),
        }
    }).then(response => {
        if (!response.ok) {
            throw response;
        }
        return response.json();
    }, rejectedError => {
        throw rejectedError.message;
    });
};

const TYPES = {
    project: {
        id: "project",
        endpoint: "/api/v1/project"
    },
    experiment: {
        id: "experiment",
        endpoint: "/api/v1/experiment"
    },
    dataset: {
        id: "dataset",
        endpoint: "/api/v1/dataset"
    },
    datafile: {
        id: "datafile",
        endpoint: "/api/v1/dataset_file"
    }
}

const getChildType = (typeId) => {
    switch(typeId) {
        case "project":
            return TYPES.experiment;
        case "experiment":
            return TYPES.dataset;
        case "dataset":
            return TYPES.datafile;
        case "datafile":
            return null;
    }
}

const getParentType = (typeId) => {
    switch(typeId) {
        case "project":
            return null;
        case "experiment":
            return TYPES.project;
        case "dataset":
            return TYPES.experiment;
        case "datafile":
            return TYPES.dataset;
    }
};

const fetchObjectsByParent = (typeId, parentId) => {
    const parentType = getParentType(typeId);
    if (!parentType) {
        throw new Error("Tried fetching resources by parent, but there is no parent.");
    }

    return fetch(`${TYPES[typeId].endpoint}/?${parentType.id}=${parentId}`, {
        method: "get",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": Cookies.get("csrftoken"),
        }
    }).then(response => {
        if (!response.ok) {
            throw response;
        }
        return response.json();
    }, rejectedError => {
        throw rejectedError.message;
    }).then(response => {
        return response.objects;
    });
};

export const validateObjectsInCart = () => {
    return (dispatch, getState) => {
        const { cart } = getState();
        const itemsInCart = cart.itemsInCart;
        dispatch(objectsValidating());
        const loadItemsPromises = itemsInCart.allIds.flatMap(typeId => {
            const itemsForType = itemsInCart.byId[typeId];
            if (!itemsForType) {
                return;
            }
            return itemsForType.map(itemId => {
                return fetchObjectById(typeId, itemId).then(object => ({
                    type: typeId,
                    object: object
                }));
            });

        });

        return Promise.all(loadItemsPromises).then((objectResults) => {
            const newObjects = {};
            objectResults.forEach(result => {
                if (!newObjects[result.type]) {
                    newObjects[result.type] = {};
                }
                newObjects[result.type][result.object.id] = result.object;
            });
            localforage.setItem("items", newObjects).then(() => {
                dispatch(objectsValidated(newObjects));
            });
        });
    };
};


// export const validateObjectsInCart = () => {
//     return (dispatch, getState) => {
// const { cartSlice } = getState();
// const itemsInCart = cartSlice.itemsInCart;
// const loadItemsPromises = itemsInCart.allIds.flatMap(typeId => {
// const itemsForType = itemsInCart.byId[typeId];
//             if (!itemsForType) {
//                 return;
//             }
//             const childType = getChildType(typeId);
// return itemsForType.map(itemId => {
//                 const fetchItemPromise = fetchObjectById(typeId, itemId).then(object => ({
//                     type: typeId,
//                     objects: [object]
//                 }));

//                 let fetchChildrenPromise = null;
//                 if (childType) {
//                     fetchChildrenPromise = fetchObjectsByParent(childType.id, itemId).then(objects => ({
//                         type: childType.id,
//                         objects
//                     }));
//                 }
//                 return [fetchItemPromise, fetchChildrenPromise];
//             });
//         });
// return Promise.all(loadItemsPromises).then((objectResults) => {
//     const newObjects = {};
//     objectResults.forEach(result => {
//         if (!newObjects[result.type]) {
//             newObjects[result.type] = {};
//         }
//         result.objects.forEach(object => {
//             newObjects[result.type][object.id] = object;
//         });
//     });
//             dispatch(objectsValidated(newObjects));
//         });
//     };
// };

/**
 * Given itemIdsByType and items, returns if each item ID in itemIdsByType has a corresponding item in the items object.
 * This determines if a cache validation is required regardless of shouldValidateCache flag.
 * @param {Object} itemIdsByType An object with byId property containing item ids by MyTardis object types, and an
 *  allIds property with MyTardis object types.
 * @param {Object} items An object with MyTardis object metadata, mapped by MyTardis object type IDs and item IDs.
 * @returns True if every item ID has corresponding item in the items object, false if not.
 */
export function eachIdHasCorrespondingItem(itemIdsByType, items) {
    if (!itemIdsByType || !items) {
        return false;
    }
    try {
        return itemIdsByType.allIds.every(typeId => {
            return itemIdsByType.byId[typeId].every(itemId => {
                return !!items[typeId][itemId];
            });
        });
    } catch (e) {
        return false;
    }
}

export const initialiseSlice = (shouldValidateCache = true) => {
    return (dispatch, getState) => {
        if(getState().cart.status !== LOADING_STATE.Initial) {
            // If the slice has already been initialised, exit.
            return;
        }
        dispatch(itemsIsLoading());
        // localforage.setItem("itemsInCart", mockCartData)
        Promise.all([
            localforage.getItem("itemIdsByType"),
            localforage.getItem("items")
        ]).then(([itemIdsByType, items]) => {
            const shouldForceRevalidateCache = !eachIdHasCorrespondingItem(itemIdsByType, items);
            dispatch(cartLoaded({
                itemIdsByType,
                items
            }));
            if (shouldValidateCache || shouldForceRevalidateCache) {
                dispatch(validateObjectsInCart());
            }
        }).catch((e) => {
            // TODO Implement fetching real data.
            console.log("Could not retrieve from cache", e);
        });
        //     return mockCartData;
        // }).then((response) => {
        //     dispatch((response));
        // }).catch(reason => { 
        //     dispatch(getItemsFailed(reason));
        // });
    };
};

export const removeItem = (typeId, id) => {
    return (dispatch, getState) => {
        dispatch(itemRemoved({typeId, id}));
        const itemsByType = getState().cart.itemsInCart;
        return localforage.setItem("itemIdsByType", itemsByType);
    };
};


const mockCartItems = {
    allIds: ["project", "experiment", "dataset"],
    byId: {
        "project": [199],
        "experiment": [61],
        "dataset": [78]
    }
};

localforage.setItem("itemIdsByType", mockCartItems); 

export default cartSlice.reducer;