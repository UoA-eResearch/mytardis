import React, { Fragment } from 'react';
import Tabs from "react-bootstrap/Tabs";
import Tab from 'react-bootstrap/Tab';
import { OBJECT_TYPE_STICKERS } from '../../TabStickers/TabSticker'
import TypeSchemaList from '../type-schema-list/TypeSchemaList';
import { runSearch } from '../../searchSlice';
import { typeAttrSelector, allTypeAttrIdsSelector, updateActiveSchemas, updateTypeAttribute } from '../filterSlice';
import { useSelector, useDispatch, batch } from "react-redux";
import PropTypes from "prop-types";
import { mapTypeToFilter } from "../index";


function TypeAttributeFilter({typeId, attributeId}) {
  const attribute = useSelector(state => (typeAttrSelector(state.filters,typeId,attributeId)));
  const dispatch = useDispatch();
  const setFilterValue = value => {
    batch(() => {
      dispatch(updateTypeAttribute({
        typeId,
        attributeId,
        value
      }));
      dispatch(runSearch());
    });
  };
  const ApplicableFilter = mapTypeToFilter(attribute.data_type);
  return (
    <section>
      <h3 className="h5">{attribute.full_name}</h3>
      <ApplicableFilter id={typeId+"."+attributeId} value={attribute.value} onValueChange={setFilterValue} options={attribute.options} />
    </section>
  )
}

TypeAttributeFilter.propTypes = {
  attribute: PropTypes.shape({
    data_type: PropTypes.string.isRequired,
    id: PropTypes.string.isRequired,
    full_name: PropTypes.string.isRequired  
  }),

}

export function TypeAttributesList({ typeId }) {
  const attributeIds = useSelector(state => (
    // Get all type attributes IDs except for schema.
    allTypeAttrIdsSelector(state.filters, typeId).filter(filterId => (filterId !== "schema"))
  ));

  return (
    <>
      {
        attributeIds.map(
          id => (
            <Fragment key={id}>
              <TypeAttributeFilter typeId={typeId} attributeId={id} />
              <hr />
            </Fragment>
          )
        )
      }
    </>
  );
}

export default function FiltersSection() {
  const typeIds = useSelector((state) => (state.filters.types.allIds));
  const isLoading = useSelector((state) => (state.filters.isLoading));
  const error = useSelector((state) => (state.filters.error));

  if (isLoading) {
    return <p>Loading filters...</p>
  }
  if (error) {
    return <p>An error occurred while loading filters.</p>
  }

  return (
    <section>
      <h2 className="h3">Filters</h2>
      <Tabs defaultActiveKey="projects" id="filters-section">
        {
          typeIds.map(type => {
            const Sticker = OBJECT_TYPE_STICKERS[type];

            return (
              <Tab key={type} eventKey={type} title={<Sticker />}>
                <TypeAttributesList typeId={type} />
                <TypeSchemaList typeId={type} />
              </Tab>
            );
          })
        }
      </Tabs>
    </section>
  )
}