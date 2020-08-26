import React, { Fragment } from 'react';
import { runSearch } from '../../searchSlice';
import { typeAttrSelector, allTypeAttrIdsSelector, updateTypeAttribute } from '../filterSlice';
import { useSelector, useDispatch, batch } from "react-redux";
import PropTypes from "prop-types";
import { mapTypeToFilter } from "../index";

function TypeAttributeFilter({ typeId, attributeId }) {
    const attribute = useSelector((state) =>
        typeAttrSelector(state.filters, typeId, attributeId)
    );
    const dispatch = useDispatch();
    const setFilterValue = (value) => {
        batch(() => {
            dispatch(
                updateTypeAttribute({
                    typeId,
                    attributeId,
                    value,
                })
            );
            dispatch(runSearch());
        });
    };
    const ApplicableFilter = mapTypeToFilter(attribute.data_type);
    return (
        <section>
            <h3 className="h5">{attribute.full_name}</h3>
            <ApplicableFilter
                id={typeId + "." + attributeId}
                value={attribute.value}
                onValueChange={setFilterValue}
                options={attribute.options}
            />
        </section>
    );
}

TypeAttributeFilter.propTypes = {
    attribute: PropTypes.shape({
        data_type: PropTypes.string.isRequired,
        id: PropTypes.string.isRequired,
        full_name: PropTypes.string.isRequired,
    }),
};

export default function TypeAttributesList({ typeId }) {
    const attributeIds = useSelector((state) =>
        // Get all type attributes IDs except for schema.
        allTypeAttrIdsSelector(state.filters, typeId).filter(
            (filterId) => filterId !== "schema"
        )
    );

    return (
        <>
            {attributeIds.map((id) => (
                <Fragment key={id}>
                    <TypeAttributeFilter typeId={typeId} attributeId={id} />
                    <hr />
                </Fragment>
            ))}
        </>
    );
}
