import { combineReducers, configureStore } from "@reduxjs/toolkit";
import cart from "@apps/cart/cartSlice";
import search from "@apps/search/components/searchSlice";
import filters from "@apps/search/components/filters/filterSlice";
import { myTardisApi } from "./api";

const rootReducer = combineReducers({cart, search, filters, [myTardisApi.reducerPath]: myTardisApi.reducer});

// Generate and keep a copy of the store on the window,
// so all different React/Redux mount points on the same page
// can share a store.
if (!window.mytardisReduxAppStore) {
    window.mytardisReduxAppStore = configureStore({
        reducer: rootReducer,
        middleware: (getDefaultMiddleware) => 
            // Adding the api middleware enables caching, invalidation, polling,
            // and other useful features of `rtk-query`.
            getDefaultMiddleware().concat(myTardisApi.middleware)
    });
}

export default window.mytardisReduxAppStore;