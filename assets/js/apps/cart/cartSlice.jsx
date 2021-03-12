import { createSlice } from "@reduxjs/toolkit";
import localforage from "localforage";
import mockCartData from "./mock-cart.json";
import Cookies from "js-cookie";

export const LOADING_STATE = {
    Initial: "INITIAL",
    LoadingFromCache: "LOADING",
    LoadedFromCache: "LOADED_FROM_CACHE",
    Finished: "FINISHED",
    Error: "ERROR"
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
    }
};

const cartSlice = createSlice({
    name: "cart",
    initialState,
    reducers: {
        itemsIsLoading: (state) => {
            state.status = LOADING_STATE.LoadingFromCache;
        },
        cartLoaded: (state, {payload}) => {
            const {itemsInCart, objects} = payload;
            if (itemsInCart) {
                state.itemsInCart = itemsInCart;
            }
            if (objects) {
                state.objects = objects;
            }
            state.status = LOADING_STATE.LoadedFromCache;
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
    cartLoaded,
    objectsValidated,
    itemsLoadFailed
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
            localforage.setItem("objects", newObjects).then(() => {
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

export const initialiseSlice = () => {
    return dispatch => {
        dispatch(itemsIsLoading());
        // localforage.setItem("itemsInCart", mockCartData)
        Promise.all([
            localforage.getItem("itemsInCart"),
            localforage.getItem("objects")
        ]).then(([itemsInCart, objects]) => {
            console.log("Items in cart in cache", itemsInCart, objects);
            dispatch(cartLoaded({
                itemsInCart,
                objects
            }));
            dispatch(validateObjectsInCart());
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


const mockCartItems = {
    allIds: ["project", "experiment", "dataset"],
    byId: {
        "project": [199],
        "experiment": [61],
        "dataset": [78]
    }
};

localforage.setItem("itemsInCart", mockCartItems); 

export default cartSlice.reducer;