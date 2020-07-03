import { combineReducers } from '@reduxjs/toolkit';

import search from './searchSlice';
import filters from "./filterSlice";

const rootReducer = combineReducers({search,filters});

export default rootReducer;