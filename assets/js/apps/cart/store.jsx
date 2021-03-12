import { combineReducers, configureStore } from "@reduxjs/toolkit";
import cart from "./cartSlice";

const rootReducer = combineReducers({cart});

const store = configureStore({
    reducer: rootReducer
});

export default store;