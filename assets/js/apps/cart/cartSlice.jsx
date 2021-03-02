import { createSlice } from "@reduxjs/toolkit";
import localforage from "localforage";
import mockCartData from "./mock-cart.json";

export const LOADING_STATE = {
    Initial: "INITIAL",
    LoadingFromCache: "LOADING_FROM_CACHE",
    Validating: "VALIDATING",
    Finished: "FINISHED",
    Error: "ERROR"
};

const initialState = {
    status: LOADING_STATE.Initial,
    itemsInCart: {
    },
    objects: {
    }
};

const cartSlice = createSlice({
    name: "cart",
    initialState,
    reducers: {
        getItemsStart: (state) => {
            state.status = LOADING_STATE.LoadingFromCache;
        },
        getItemsLoadedFromCache: (state, {payload}) => {
            const {itemsInCart, objects} = payload;
            state.itemsInCart = itemsInCart;
            state.objects = objects;
            state.status = LOADING_STATE.Validating;
        },
        getItemsValidated: (state, {payload}) => {
            const {itemsInCart, objects} = payload;
            state.itemsInCart = itemsInCart;
            state.objects = objects;
            state.status = LOADING_STATE.Finished;
        },
        getItemsFailed: (state => {
            state.status = LOADING_STATE.Error;
        },
        removeItem: (state, {payload}) => {
            const {typeId, id} = payload;
            state.
        }
    }
});

export const {
    getItemsStart,
    getItemsLoadedFromCache,
    getItemsValidated,
    getItemsFailed
} = cartSlice.actions;


export const initialiseSlice = () => {
    return dispatch => {
        dispatch(getItemsStart());
        Promise.all([
            localforage.getItem("itemsInCart"),
            localforage.getItem("objects")
        ]).then(([itemsInCart, objects]) => {
            console.log("Items in cart in cache", itemsInCart);
            dispatch(getItemsLoadedFromCache({
                itemsInCart,
                objects
            }));
        }).then(() => {
            // TODO Implement fetching real data.
            return mockCartData;
        }).then((response) => {
            dispatch(getItemsValidated(response));
            // Update local cache.
            console.log("Updating local cache.");
            localforage.setItem("itemsInCart", response.itemsInCart);
            localforage.setItem("objects", response.objects);
        }).catch(reason => {
            dispatch(getItemsFailed(reason));
        });
    };
};

export default cartSlice.reducer;