// L1.test.js
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom'; // For extended matchers like .toBeInTheDocument()

import L1 from './L1'; // Adjust the path if your component is in a different directory

describe('L1 Component', () => {
  // Mock the handlLabelClick function before each test
  let mockHandlLabelClick;

  beforeEach(() => {
    mockHandlLabelClick = jest.fn(); // Create a fresh mock function for each test
  });

  // --- 1. Test Rendering with Props ---

  describe('when tracking prop is true', () => {
    it('renders the tracking labels and static elements', () => {
      render(<L1 tracking={true} handlLabelClick={mockHandlLabelClick} />);

      // Check for static background images (using alt text or src if available)
      // Since your images don't have alt text, we'll check by src attribute
      expect(screen.getByRole('img', { name: /^NavBarBg$/i })).toBeInTheDocument();
      expect(screen.getByRole('img', { name: /^ProgressBarBg$/i })).toBeInTheDocument();
      expect(screen.getByRole('img', { name: /^NavMeasurementsBG$/i })).toBeInTheDocument();
      expect(screen.getByRole('img', { name: /^Logo$/i })).toBeInTheDocument();
      expect(screen.getByRole('img', { name: /^PatientDataBg$/i })).toBeInTheDocument();
      expect(screen.getByRole('img', { name: /^PatientIcon$/i })).toBeInTheDocument();

      // Check for tracking-specific labels
      const apLabel = screen.getByRole('img', { name: /^APLabel$/i });
      const obLabel = screen.getByRole('img', { name: /^OBLabel$/i });

      expect(apLabel).toBeInTheDocument();
      expect(obLabel).toBeInTheDocument();

      // Assert that manual labels are NOT present
      expect(screen.queryByRole('img', { name: /^ManualAPLabel$/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('img', { name: /^ManualOBLabel$/i })).not.toBeInTheDocument();
    });

    it('matches snapshot when tracking is true', () => {
      const { asFragment } = render(<L1 tracking={true} handlLabelClick={mockHandlLabelClick} />);
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe('when tracking prop is false', () => {
    it('renders the manual labels and static elements', () => {
      render(<L1 tracking={false} handlLabelClick={mockHandlLabelClick} />);

      // Check for static background images (same as above)
      expect(screen.getByRole('img', { name: /^NavBarBg$/i })).toBeInTheDocument();
      expect(screen.getByRole('img', { name: /^ProgressBarBg$/i })).toBeInTheDocument();
      expect(screen.getByRole('img', { name: /^NavMeasurementsBG$/i })).toBeInTheDocument();
      expect(screen.getByRole('img', { name: /^Logo$/i })).toBeInTheDocument();
      expect(screen.getByRole('img', { name: /^PatientDataBg$/i })).toBeInTheDocument();
      expect(screen.getByRole('img', { name: /^PatientIcon$/i })).toBeInTheDocument();

      // Check for manual-specific labels and their backgrounds
      const manualApLabelBg = screen.getByRole('img', { name: /^ManualAPLabelBg$/i });
      const manualApLabel = screen.getByRole('img', { name: /^ManualAPLabel$/i });
      const manualObLabelBg = screen.getByRole('img', { name: /^ManualOBLabelBg$/i });
      const manualObLabel = screen.getByRole('img', { name: /^ManualOBLabel$/i });

      expect(manualApLabelBg).toBeInTheDocument();
      expect(manualApLabel).toBeInTheDocument();
      expect(manualObLabelBg).toBeInTheDocument();
      expect(manualObLabel).toBeInTheDocument();

      // Assert that tracking labels are NOT present
      expect(screen.queryByRole('img', { name: /^APLabel$/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('img', { name: /^OBLabel$/i })).not.toBeInTheDocument();
    });

    it('matches snapshot when tracking is false', () => {
      const { asFragment } = render(<L1 tracking={false} handlLabelClick={mockHandlLabelClick} />);
      expect(asFragment()).toMatchSnapshot();
    });
  });

  // --- 2. Test User Interactions ---

  describe('Interaction when tracking prop is false', () => {
    it('calls handlLabelClick with "ap" when the Manual AP Label is clicked', () => {
      render(<L1 tracking={false} handlLabelClick={mockHandlLabelClick} />);

      const manualApLabel = screen.getByRole('img', { name: /^ManualAPLabel$/i });

      fireEvent.click(manualApLabel);

      expect(mockHandlLabelClick).toHaveBeenCalledTimes(1);
      expect(mockHandlLabelClick).toHaveBeenCalledWith('ap');
    });

    it('calls handlLabelClick with "ob" when the Manual OB Label is clicked', () => {
      render(<L1 tracking={false} handlLabelClick={mockHandlLabelClick} />);

      const manualObLabel = screen.getByRole('img', { name: /^ManualOBLabel$/i });

      fireEvent.click(manualObLabel);

      expect(mockHandlLabelClick).toHaveBeenCalledTimes(1);
      expect(mockHandlLabelClick).toHaveBeenCalledWith('ob');
    });

    it('does not call handlLabelClick when elements without click handlers are clicked', () => {
        // This test ensures that only the intended elements trigger the callback.
        // It implicitly covers that when `tracking` is true, nothing is clickable.
        render(<L1 tracking={false} handlLabelClick={mockHandlLabelClick} />);

        // Click on a background image that doesn't have a click handler
        const navBarBg = screen.getByRole('img', { name: /^NavBarBg$/i });
        fireEvent.click(navBarBg);

        expect(mockHandlLabelClick).not.toHaveBeenCalled();
    });
  });

  describe('Interaction when tracking prop is true (no click interaction expected)', () => {
    it('does not call handlLabelClick when tracking labels are present', () => {
      render(<L1 tracking={true} handlLabelClick={mockHandlLabelClick} />);

      // Attempt to click the APLabel and OBLabel, which should not have click handlers
      const apLabel = screen.getByRole('img', { name: /^APLabel$/i });
      const obLabel = screen.getByRole('img', { name: /^OBLabel$/i });

      // Note: fireEvent.click will still trigger if an element is clicked,
      // but the `handlLabelClick` will only be called if there's an `onClick` prop
      // on that specific element. In this case, there isn't, so the mock shouldn't be called.
      fireEvent.click(apLabel);
      fireEvent.click(obLabel);

      expect(mockHandlLabelClick).not.toHaveBeenCalled();
    });
  });
});