// L7.test.js
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom'; // For extended matchers like .toBeInTheDocument()

import L7 from './L7'; // Adjust the path if your component is in a different directory


describe('L7 Component - Static Elements', () => {
  // Section 1: Test Rendering of Static Elements

  it('renders all static toolbar and button background images with correct alt text', () => {
    // Render the component with all props as null or no-op functions for initial test
    render(
      <L7
        handledit={() => {}}
        setReport={() => {}}
        leftCheckMark={null}
        rightCheckMark={null}
        recon={null}
        setPause={() => {}}
      />
    );

    // Verify presence of static images using their alt text
    // Note: ensure the alt texts in the component match these expectations
    expect(screen.getByRole('img', { name: /Imaging Mode Toolbar/i })).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /edit icon/i })).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /Report Icon/i })).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /acquire icon/i,  hidden: true })).toBeInTheDocument(); // For PauseButtonBg
    expect(screen.getByRole('img', { name: /acquire icon/i })).toBeInTheDocument(); // For PauseButton

    // To differentiate the two "acquire icon" elements, you might need to be more specific,
    // or add more descriptive alt text in the component.
    // For now, we're checking if both are present.
    // The `hidden: true` is an attempt to target the background more specifically if needed,
    // but a unique alt text is always better for clarity.
  });

  it('matches snapshot for default rendering (all dynamic icons null)', () => {
    const { asFragment } = render(
      <L7
        handledit={() => {}}
        setReport={() => {}}
        leftCheckMark={null}
        rightCheckMark={null}
        recon={null}
        setPause={() => {}}
      />
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
