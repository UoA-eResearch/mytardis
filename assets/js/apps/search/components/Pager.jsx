import React from 'react';
import PropTypes from "prop-types";
import { Pagination } from "react-bootstrap";
import { pageSizeSelector, pageNumberSelector, updatePageSize, updatePageNumber } from "./searchSlice";
import { useSelector } from "react-redux";

function Pager({objectType}) {
    const pageNum = useSelector(state => (
        pageNumberSelector(state.search,objectType)
    ));
    const pageSize = useSelector(state => (
        pageSizeSelector(state.search, objectType)
    ));
    return (
        <Pagination>
            <Pagination.Item>{pageNum}</Pagination.Item>
        </Pagination>
    );
}

Pager.propTypes = {
    objectType: PropTypes.string.isRequired
};

export default Pager;