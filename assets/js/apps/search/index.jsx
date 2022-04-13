import React from 'react';
import ReactDOM from 'react-dom';
import SearchPage from './components/SearchPage';
import store from "@apps/shared/reduxAppStore";
import { Provider } from 'react-redux';

ReactDOM.render(
  (<Provider store={store}>
    <SearchPage />
  </Provider>),
  document.getElementById('search-app'),
);
